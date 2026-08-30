"""Fair replay-only baseline."""

from __future__ import annotations

from fidelitygate.environment import build_environment
from fidelitygate.models import CaseResult, CaseSpec, Verdict


def run_replay_baseline(case: CaseSpec) -> CaseResult:
    """Accept when every supplied expert trace executes without contradiction."""
    environment = build_environment(case)
    transitions = 0
    for trace_index, trace in enumerate(case.expert_traces):
        state = environment.initial_state()
        for action_index, action in enumerate(trace):
            state, observation = environment.step(state, action)
            transitions += 1
            violation = environment.check_claims(state)
            if not observation.accepted or violation is not None:
                detail = (
                    f"Expert trace {trace_index} failed at action {action_index}: "
                    f"{action.display()}."
                )
                return CaseResult(
                    case_id=case.id,
                    ground_truth=case.ground_truth,
                    verdict=Verdict.REJECT,
                    reason=detail,
                    explored_states=trace_index + 1,
                    explored_transitions=transitions,
                    search_complete=True,
                )

    return CaseResult(
        case_id=case.id,
        ground_truth=case.ground_truth,
        verdict=Verdict.ACCEPT,
        reason="All supplied expert trajectories completed without a claim contradiction.",
        explored_states=len(case.expert_traces),
        explored_transitions=transitions,
        search_complete=True,
    )
