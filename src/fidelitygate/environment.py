"""Safe declarative environment adapter and fixture-registry validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TypeVar

from fidelitygate.models import (
    Action,
    AuditCaseSpec,
    ClaimViolation,
    ComparisonOp,
    Condition,
    Effect,
    EffectOp,
    FixtureRegistry,
    FixtureSpec,
    Observation,
    Primitive,
)

StateT = TypeVar("StateT")


class EnvironmentAdapter(Protocol[StateT]):
    def initial_state(self) -> StateT: ...

    def actions(self, state: StateT) -> tuple[Action, ...]: ...

    def step(self, state: StateT, action: Action) -> tuple[StateT, Observation]: ...

    def state_key(self, state: StateT) -> tuple[object, ...]: ...

    def check_claims(self, state: StateT) -> ClaimViolation | None: ...

    def claim_progress(self, state: StateT) -> int: ...


@dataclass(frozen=True, slots=True)
class WorkflowState:
    """Immutable normalized state with a stable canonical key."""

    values: tuple[tuple[str, Primitive], ...]

    @classmethod
    def from_mapping(cls, values: Mapping[str, Primitive]) -> WorkflowState:
        return cls(tuple(sorted(values.items())))

    def as_dict(self) -> dict[str, Primitive]:
        return dict(self.values)


class DeclarativeEnvironment:
    """Execute a finite workflow DSL without eval, imports, I/O, or arbitrary code."""

    def __init__(self, case: AuditCaseSpec, fixture: FixtureSpec) -> None:
        self.case = case
        self.fixture = fixture
        self._validate_fixture()

    def initial_state(self) -> WorkflowState:
        return WorkflowState.from_mapping(self.fixture.initial_state)

    def actions(self, state: WorkflowState) -> tuple[Action, ...]:
        del state
        return tuple(self.fixture.actions)

    def state_key(self, state: WorkflowState) -> tuple[object, ...]:
        return tuple(state.values)

    def step(self, state: WorkflowState, action: Action) -> tuple[WorkflowState, Observation]:
        values = state.as_dict()
        matching_rules = [rule for rule in self.fixture.rules if rule.action == action]
        for rule in matching_rules:
            if not all(evaluate_condition(condition, values) for condition in rule.requires):
                continue
            next_values = dict(values)
            for effect in rule.effects:
                apply_effect(effect, next_values)
            return WorkflowState.from_mapping(next_values), Observation(
                accepted=True,
                event=rule.event,
                details={"action": action.display()},
            )
        return state, Observation(
            accepted=False,
            event="action_denied",
            details={"action": action.display()},
        )

    def check_claims(self, state: WorkflowState) -> ClaimViolation | None:
        values = state.as_dict()
        for claim in self.case.claims:
            if all(evaluate_condition(condition, values) for condition in claim.forbidden_when):
                observed = ", ".join(
                    f"{condition.field}={values[condition.field]!r}"
                    for condition in claim.forbidden_when
                )
                return ClaimViolation(
                    claim_id=claim.id,
                    statement=claim.statement,
                    source=claim.source,
                    source_excerpt=claim.source_excerpt,
                    expected=f"Forbidden state is unreachable: {claim.statement}",
                    observed=f"Reached state satisfying forbidden pattern: {observed}",
                )
        return None

    def claim_progress(self, state: WorkflowState) -> int:
        """Count satisfied forbidden-state clauses for claim-directed prioritization."""
        values = state.as_dict()
        return max(
            sum(evaluate_condition(condition, values) for condition in claim.forbidden_when)
            for claim in self.case.claims
        )

    def _validate_fixture(self) -> None:
        fields = set(self.fixture.initial_state)
        if not fields:
            raise ValueError("fixture initial_state cannot be empty")
        action_encodings = {action.model_dump_json() for action in self.fixture.actions}
        if len(action_encodings) != len(self.fixture.actions):
            raise ValueError("fixture action alphabet contains duplicates")
        for rule in self.fixture.rules:
            if rule.action.model_dump_json() not in action_encodings:
                raise ValueError(f"rule references undeclared action: {rule.action.display()}")
            self._validate_fields(rule.requires, fields)
            for effect in rule.effects:
                if effect.field not in fields:
                    raise ValueError(f"effect references unknown field: {effect.field}")
        for claim in self.case.claims:
            self._validate_fields(claim.forbidden_when, fields)

    @staticmethod
    def _validate_fields(conditions: list[Condition], fields: set[str]) -> None:
        for condition in conditions:
            if condition.field not in fields:
                raise ValueError(f"condition references unknown field: {condition.field}")


def evaluate_condition(condition: Condition, state: Mapping[str, Primitive]) -> bool:
    left = state[condition.field]
    right = condition.value
    if condition.op == ComparisonOp.EQ:
        return left == right
    if condition.op == ComparisonOp.NE:
        return left != right
    if isinstance(left, bool) or isinstance(right, bool):
        raise TypeError(f"ordered comparison is invalid for booleans: {condition.field}")
    if not isinstance(left, int | float) or not isinstance(right, int | float):
        raise TypeError(f"ordered comparison requires numbers: {condition.field}")
    if condition.op == ComparisonOp.GT:
        return left > right
    if condition.op == ComparisonOp.GTE:
        return left >= right
    if condition.op == ComparisonOp.LT:
        return left < right
    if condition.op == ComparisonOp.LTE:
        return left <= right
    raise AssertionError(f"unhandled comparison operator: {condition.op}")


def apply_effect(effect: Effect, state: dict[str, Primitive]) -> None:
    if effect.op == EffectOp.SET:
        state[effect.field] = effect.value
        return
    current = state[effect.field]
    if (
        isinstance(current, bool)
        or isinstance(effect.value, bool)
        or not isinstance(current, int | float)
        or not isinstance(effect.value, int | float)
    ):
        raise TypeError(f"increment requires numeric state: {effect.field}")
    state[effect.field] = current + effect.value


def load_fixture_registry(path: Path) -> tuple[FixtureRegistry, str]:
    """Strictly validate a fixture registry and return its SHA-256."""
    import hashlib

    raw = path.read_bytes()
    registry = FixtureRegistry.model_validate_json(raw)
    return registry, hashlib.sha256(raw).hexdigest()


def resolve_registry_path(suite_path: Path, configured: str) -> Path:
    """Resolve only paths inside the evaluation data root."""
    evaluation_root = suite_path.resolve().parent.parent
    candidate = (suite_path.parent / configured).resolve()
    if not candidate.is_relative_to(evaluation_root):
        raise ValueError("fixture registry must stay inside the evaluation data root")
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def build_environment(case: AuditCaseSpec, registry: FixtureRegistry) -> DeclarativeEnvironment:
    try:
        fixture = registry.fixtures[case.fixture_id]
    except KeyError as error:
        raise ValueError(f"unknown fixture ID: {case.fixture_id}") from error
    return DeclarativeEnvironment(case, fixture)


def fixture_registry_as_canonical_json(registry: FixtureRegistry) -> str:
    """Stable serialization helper used by sandbox workers and tests."""
    return json.dumps(registry.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
