"""Environment adapter protocol and the synthetic refund workflow."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol, TypeVar

from fidelitygate.models import Action, CaseSpec, ClaimViolation, Observation

StateT = TypeVar("StateT")


class EnvironmentAdapter(Protocol[StateT]):
    """Narrow contract needed by deterministic exploration."""

    def initial_state(self) -> StateT: ...

    def actions(self, state: StateT) -> tuple[Action, ...]: ...

    def step(self, state: StateT, action: Action) -> tuple[StateT, Observation]: ...

    def state_key(self, state: StateT) -> tuple[object, ...]: ...

    def check_claims(self, state: StateT) -> ClaimViolation | None: ...


@dataclass(frozen=True, slots=True)
class RefundState:
    """Complete synthetic state exposed to the harness."""

    amount: int | None = None
    manager_approved: bool = False
    issued: bool = False


class RefundEnvironment:
    """Deterministic refund workflow with an optional approval-bypass defect."""

    HIGH_VALUE_THRESHOLD = 1_000

    def __init__(self, case: CaseSpec) -> None:
        if case.adapter != "refund":
            raise ValueError(f"unsupported adapter: {case.adapter}")
        self.case = case
        self._admin_bypass = case.mutation == "admin_approval_bypass"
        self._action_alphabet = (
            Action(name="submit_refund", arguments={"amount": 50}),
            Action(name="submit_refund", arguments={"amount": 1_500}),
            Action(name="approve_refund", arguments={"role": "operator"}),
            Action(name="approve_refund", arguments={"role": "manager"}),
            Action(name="issue_refund", arguments={"role": "operator"}),
            Action(name="issue_refund", arguments={"role": "admin"}),
        )

    def initial_state(self) -> RefundState:
        return RefundState()

    def actions(self, state: RefundState) -> tuple[Action, ...]:
        del state
        return self._action_alphabet

    def state_key(self, state: RefundState) -> tuple[object, ...]:
        return (state.amount, state.manager_approved, state.issued)

    def step(self, state: RefundState, action: Action) -> tuple[RefundState, Observation]:
        if action.name == "submit_refund":
            return self._submit(state, action)
        if action.name == "approve_refund":
            return self._approve(state, action)
        if action.name == "issue_refund":
            return self._issue(state, action)
        return state, Observation(accepted=False, event="unknown_action")

    def check_claims(self, state: RefundState) -> ClaimViolation | None:
        high_value_without_approval = (
            state.issued
            and state.amount is not None
            and state.amount > self.HIGH_VALUE_THRESHOLD
            and not state.manager_approved
        )
        if not high_value_without_approval:
            return None

        claim = next(
            claim for claim in self.case.claims if claim.id == "refund.high_value_approval"
        )
        return ClaimViolation(
            claim_id=claim.id,
            statement=claim.statement,
            source=claim.source,
            expected="A refund above $1,000 is issued only after manager approval.",
            observed=(f"A ${state.amount:,} refund was issued while manager_approved=false."),
        )

    @staticmethod
    def _submit(state: RefundState, action: Action) -> tuple[RefundState, Observation]:
        amount = action.arguments.get("amount")
        if state.amount is not None or not isinstance(amount, int) or amount <= 0:
            return state, Observation(accepted=False, event="refund_submission_denied")
        return replace(state, amount=amount), Observation(
            accepted=True,
            event="refund_submitted",
            details={"amount": amount},
        )

    @staticmethod
    def _approve(state: RefundState, action: Action) -> tuple[RefundState, Observation]:
        role = action.arguments.get("role")
        if state.amount is None or state.issued or role != "manager":
            return state, Observation(
                accepted=False,
                event="refund_approval_denied",
                details={"role": role},
            )
        return replace(state, manager_approved=True), Observation(
            accepted=True,
            event="refund_approved",
            details={"role": role},
        )

    def _issue(self, state: RefundState, action: Action) -> tuple[RefundState, Observation]:
        role = action.arguments.get("role")
        if state.amount is None or state.issued or role not in {"operator", "admin"}:
            return state, Observation(
                accepted=False,
                event="refund_issue_denied",
                details={"role": role},
            )

        requires_approval = state.amount > self.HIGH_VALUE_THRESHOLD
        bypass_applies = self._admin_bypass and role == "admin"
        if requires_approval and not state.manager_approved and not bypass_applies:
            return state, Observation(
                accepted=False,
                event="refund_issue_denied",
                details={"role": role, "reason": "manager_approval_required"},
            )

        return replace(state, issued=True), Observation(
            accepted=True,
            event="refund_issued",
            details={"amount": state.amount, "role": role},
        )


def build_environment(case: CaseSpec) -> RefundEnvironment:
    """Construct a repository-owned adapter from a validated case."""
    if case.adapter == "refund":
        return RefundEnvironment(case)
    raise ValueError(f"unsupported adapter: {case.adapter}")
