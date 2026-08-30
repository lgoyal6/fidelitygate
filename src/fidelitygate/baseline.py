"""Fair baselines that never receive benchmark labels."""

from __future__ import annotations

import hashlib
import random

from fidelitygate.environment import build_environment
from fidelitygate.models import (
    Action,
    AuditCaseSpec,
    AuditOutcome,
    FixtureRegistry,
    Verdict,
    Witness,
)
from fidelitygate.replay import replay_for_violation, replay_trace, shrink_actions


def run_replay_baseline(case: AuditCaseSpec, registry: FixtureRegistry) -> AuditOutcome:
    """Accept when every supplied expert trace executes without contradiction."""
    environment = build_environment(case, registry)
    transitions = 0
    claim_checks = 0
    for trace_index, trace in enumerate(case.expert_traces):
        state = environment.initial_state()
        claim_checks += 1
        for action_index, action in enumerate(trace):
            state, observation = environment.step(state, action)
            transitions += 1
            violation = environment.check_claims(state)
            claim_checks += 1
            if not observation.accepted or violation is not None:
                detail = (
                    f"Expert trace {trace_index} failed at action {action_index}: "
                    f"{action.display()}."
                )
                return AuditOutcome(
                    case_id=case.id,
                    verdict=Verdict.REJECT,
                    reason=detail,
                    explored_states=trace_index + 1,
                    explored_transitions=transitions,
                    claim_checks=claim_checks,
                    search_complete=True,
                )

    return AuditOutcome(
        case_id=case.id,
        verdict=Verdict.ACCEPT,
        reason="All supplied expert trajectories completed without a claim contradiction.",
        explored_states=len(case.expert_traces),
        explored_transitions=transitions,
        claim_checks=claim_checks,
        search_complete=True,
    )


def run_random_baseline(case: AuditCaseSpec, registry: FixtureRegistry, seed: int) -> AuditOutcome:
    """Budgeted deterministic random sequences for an exploration baseline."""
    environment = build_environment(case, registry)
    seed_material = f"{seed}:{case.id}".encode()
    case_seed = int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big")
    generator = random.Random(case_seed)
    transitions = 0
    claim_checks = 0
    sequences = 0
    alphabet = environment.actions(environment.initial_state())

    while transitions < case.max_transitions:
        length = generator.randint(1, case.max_depth)
        sequence: list[Action] = []
        for _ in range(length):
            if transitions >= case.max_transitions:
                break
            sequence.append(generator.choice(alphabet))
            transitions += 1
        sequences += 1
        _, violation = replay_trace(environment, sequence)
        claim_checks += len(sequence) + 1
        if violation is None:
            continue
        minimized = shrink_actions(
            sequence,
            lambda actions: replay_for_violation(environment, actions) is not None,
        )
        replayed = replay_for_violation(environment, minimized)
        if replayed is None:
            return AuditOutcome(
                case_id=case.id,
                verdict=Verdict.UNKNOWN,
                reason="Random exploration observed a contradiction that failed replay.",
                explored_states=sequences,
                explored_transitions=transitions,
                claim_checks=claim_checks,
                search_complete=False,
            )
        return AuditOutcome(
            case_id=case.id,
            verdict=Verdict.REJECT,
            reason=f"Random exploration found a contradiction for {replayed.claim_id}.",
            explored_states=sequences,
            explored_transitions=transitions,
            claim_checks=claim_checks,
            search_complete=False,
            witness=Witness(
                actions=minimized,
                violation=replayed,
                replayable=True,
                replay_attempts=1,
                replay_successes=1,
                original_length=len(sequence),
                minimized_length=len(minimized),
            ),
        )

    return AuditOutcome(
        case_id=case.id,
        verdict=Verdict.UNKNOWN,
        reason=(
            "Budgeted random exploration found no contradiction but cannot establish completeness."
        ),
        explored_states=sequences,
        explored_transitions=transitions,
        claim_checks=claim_checks,
        search_complete=False,
    )
