"""Deterministic bounded falsification kernel."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from fidelitygate.environment import RefundState, build_environment
from fidelitygate.models import Action, CaseResult, CaseSpec, Verdict, Witness
from fidelitygate.replay import replay_for_violation, shrink_actions


@dataclass(frozen=True, slots=True)
class FrontierNode:
    state: RefundState
    actions: tuple[Action, ...]


def audit_case(case: CaseSpec) -> CaseResult:
    """Explore the finite reachable graph and return the first shortest contradiction."""
    environment = build_environment(case)
    initial = environment.initial_state()
    queue = deque([FrontierNode(state=initial, actions=())])
    seen = {environment.state_key(initial)}
    transitions = 0
    depth_truncated = False
    state_limit_hit = False

    initial_violation = environment.check_claims(initial)
    if initial_violation is not None:
        witness = Witness(
            actions=[],
            violation=initial_violation,
            replayable=replay_for_violation(environment, []) is not None,
            original_length=0,
            minimized_length=0,
        )
        return _rejection(case, witness, len(seen), transitions)

    while queue:
        node = queue.popleft()
        for action in environment.actions(node.state):
            next_state, _ = environment.step(node.state, action)
            transitions += 1
            next_actions = (*node.actions, action)
            key = environment.state_key(next_state)
            if len(next_actions) > case.max_depth:
                if key not in seen:
                    depth_truncated = True
                continue
            violation = environment.check_claims(next_state)
            if violation is not None:
                minimized = shrink_actions(
                    next_actions,
                    lambda actions: replay_for_violation(environment, actions) is not None,
                )
                replayed = replay_for_violation(environment, minimized)
                if replayed is None:
                    return CaseResult(
                        case_id=case.id,
                        ground_truth=case.ground_truth,
                        verdict=Verdict.UNKNOWN,
                        reason=(
                            "A contradiction was observed but its minimized witness did not replay."
                        ),
                        explored_states=len(seen),
                        explored_transitions=transitions,
                        search_complete=False,
                    )
                witness = Witness(
                    actions=minimized,
                    violation=replayed,
                    replayable=True,
                    original_length=len(next_actions),
                    minimized_length=len(minimized),
                )
                return _rejection(case, witness, len(seen), transitions)

            if key in seen:
                continue
            if len(seen) >= case.max_states:
                state_limit_hit = True
                continue
            seen.add(key)
            queue.append(FrontierNode(state=next_state, actions=next_actions))

    if depth_truncated or state_limit_hit:
        reasons = []
        if depth_truncated:
            reasons.append(f"new reachable states exceeded max_depth={case.max_depth}")
        if state_limit_hit:
            reasons.append(f"state exploration reached max_states={case.max_states}")
        return CaseResult(
            case_id=case.id,
            ground_truth=case.ground_truth,
            verdict=Verdict.UNKNOWN,
            reason="Search incomplete: " + "; ".join(reasons) + ".",
            explored_states=len(seen),
            explored_transitions=transitions,
            search_complete=False,
        )

    return CaseResult(
        case_id=case.id,
        ground_truth=case.ground_truth,
        verdict=Verdict.ACCEPT,
        reason="No contradiction exists in the completely explored finite reachable graph.",
        explored_states=len(seen),
        explored_transitions=transitions,
        search_complete=True,
    )


def _rejection(
    case: CaseSpec,
    witness: Witness,
    states: int,
    transitions: int,
) -> CaseResult:
    return CaseResult(
        case_id=case.id,
        ground_truth=case.ground_truth,
        verdict=Verdict.REJECT,
        reason=f"Replayable contradiction found for claim {witness.violation.claim_id}.",
        explored_states=states,
        explored_transitions=transitions,
        search_complete=False,
        witness=witness,
    )
