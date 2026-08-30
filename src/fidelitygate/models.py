"""Typed contracts shared by suites, adapters, agents, and reports."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Primitive = str | int | float | bool | None


class StrictModel(BaseModel):
    """Forbid silent schema drift in evidence and environment packages."""

    model_config = ConfigDict(extra="forbid")


class Verdict(StrEnum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class GroundTruth(StrEnum):
    CLEAN = "clean"
    MUTATED = "mutated"


class ComparisonOp(StrEnum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"


class EffectOp(StrEnum):
    SET = "set"
    INCREMENT = "increment"


class Action(StrictModel):
    """A schema-validated action supplied to an environment adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    arguments: dict[str, Primitive] = Field(default_factory=dict)

    def display(self) -> str:
        if not self.arguments:
            return self.name
        args = ", ".join(f"{key}={self.arguments[key]!r}" for key in sorted(self.arguments))
        return f"{self.name}({args})"


class Condition(StrictModel):
    """A safe comparison over one normalized state field."""

    field: str
    op: ComparisonOp
    value: Primitive


class Effect(StrictModel):
    """A typed state update; arbitrary code is not accepted by the fixture DSL."""

    field: str
    op: EffectOp = EffectOp.SET
    value: Primitive

    @model_validator(mode="after")
    def increment_requires_number(self) -> Effect:
        if self.op == EffectOp.INCREMENT and (
            not isinstance(self.value, int | float) or isinstance(self.value, bool)
        ):
            raise ValueError("increment effects require a numeric value")
        return self


class RuleSpec(StrictModel):
    """One valid action transition in a declarative environment."""

    action: Action
    requires: list[Condition] = Field(default_factory=list)
    effects: list[Effect] = Field(default_factory=list)
    event: str


class FixtureSpec(StrictModel):
    """Finite-state synthetic environment package."""

    initial_state: dict[str, Primitive]
    actions: list[Action]
    rules: list[RuleSpec]


class FixtureRegistry(StrictModel):
    """Opaque fixture IDs keep benchmark labels out of system interfaces."""

    schema_version: Literal["1"]
    fixtures: dict[str, FixtureSpec]


class ClaimSpec(StrictModel):
    """A source-grounded state pattern that must never become reachable."""

    id: str
    statement: str
    source: str
    source_excerpt: str
    severity: Literal["low", "medium", "high", "critical"]
    forbidden_when: Annotated[list[Condition], Field(min_length=1)]


class AuditCaseSpec(StrictModel):
    """Unlabeled input visible to a system under evaluation."""

    id: str
    fixture_id: str
    max_depth: Annotated[int, Field(ge=1, le=50)]
    max_states: Annotated[int, Field(ge=1, le=100_000)] = 10_000
    max_transitions: Annotated[int, Field(ge=1, le=1_000_000)] = 100_000
    expert_traces: list[list[Action]]
    claims: Annotated[list[ClaimSpec], Field(min_length=1)]


class CaseSpec(AuditCaseSpec):
    """Benchmark case with evaluator-only ground truth."""

    ground_truth: GroundTruth
    family: str
    critical: bool = False

    def audit_input(self) -> AuditCaseSpec:
        """Remove labels before invoking the system under evaluation."""
        return AuditCaseSpec.model_validate(
            self.model_dump(exclude={"ground_truth", "family", "critical"})
        )


class SuiteSpec(StrictModel):
    schema_version: Literal["1"]
    id: str
    description: str
    fixture_registry: str
    cases: Annotated[list[CaseSpec], Field(min_length=2)]


class Observation(StrictModel):
    accepted: bool
    event: str
    details: dict[str, Primitive] = Field(default_factory=dict)


class ClaimViolation(StrictModel):
    claim_id: str
    statement: str
    source: str
    source_excerpt: str
    expected: str
    observed: str


class Witness(StrictModel):
    actions: list[Action]
    violation: ClaimViolation
    replayable: bool
    replay_attempts: Annotated[int, Field(ge=0)]
    replay_successes: Annotated[int, Field(ge=0)]
    original_length: Annotated[int, Field(ge=0)]
    minimized_length: Annotated[int, Field(ge=0)]


class AuditOutcome(StrictModel):
    """Unlabeled system output; it cannot use benchmark truth by construction."""

    case_id: str
    verdict: Verdict
    reason: str
    explored_states: Annotated[int, Field(ge=0)]
    explored_transitions: Annotated[int, Field(ge=0)]
    claim_checks: Annotated[int, Field(ge=0)]
    search_complete: bool
    witness: Witness | None = None


class AgentEvent(StrictModel):
    sequence: Annotated[int, Field(ge=1)]
    phase: Literal["orient", "explore", "verify", "decide"]
    tool: str
    details: dict[str, Primitive]


class AgentTrajectory(StrictModel):
    schema_version: Literal["1"] = "1"
    agent: Literal["fidelitygate-falsification-agent"]
    instruction: str
    case_id: str
    events: list[AgentEvent]
    outcome: AuditOutcome


class CaseResult(AuditOutcome):
    ground_truth: GroundTruth
    family: str
    critical: bool


class Metrics(StrictModel):
    balanced_accuracy: float
    clean_specificity: float
    mutant_recall: float
    critical_mutant_recall: float | None
    unknown_rate: float
    replay_success_rate: float
    median_witness_length: float | None
    clean_total: int
    mutated_total: int
    correct_clean: int
    correct_mutated: int
    unknown_count: int
    family_recall: dict[str, float]


class EvaluationReport(StrictModel):
    schema_version: Literal["2"] = "2"
    suite_id: str
    suite_sha256: str
    fixture_registry_sha256: str
    evidence_sha256: dict[str, str]
    system: Literal["replay-baseline", "random-baseline", "bfs-ablation", "fidelitygate"]
    seed: int
    results: list[CaseResult]
    metrics: Metrics
