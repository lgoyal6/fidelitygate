"""Deterministic falsification agent with coverage memory and replay verification."""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass
from typing import Literal, Protocol

from fidelitygate.environment import DeclarativeEnvironment, WorkflowState, build_environment
from fidelitygate.models import (
    Action,
    AuditCaseSpec,
    AuditOutcome,
    FixtureRegistry,
    Primitive,
    Verdict,
    Witness,
)
from fidelitygate.replay import replay_for_violation, shrink_actions


class EventSink(Protocol):
    def emit(self, phase: str, tool: str, details: dict[str, Primitive]) -> None: ...


@dataclass(frozen=True, slots=True)
class FrontierNode:
    state: WorkflowState
    actions: tuple[Action, ...]


class SearchFrontier:
    """BFS ablation or claim-directed best-first memory behind one interface."""

    def __init__(self, strategy: Literal["guided", "bfs"]) -> None:
        self.strategy = strategy
        self.queue: deque[FrontierNode] = deque()
        self.heap: list[tuple[int, int, int, FrontierNode]] = []
        self.serial = 0

    def push(self, node: FrontierNode, progress: int) -> None:
        if self.strategy == "bfs":
            self.queue.append(node)
            return
        self.serial += 1
        heapq.heappush(self.heap, (-progress, len(node.actions), self.serial, node))

    def pop(self) -> FrontierNode:
        if self.strategy == "bfs":
            return self.queue.popleft()
        return heapq.heappop(self.heap)[-1]

    def __bool__(self) -> bool:
        return bool(self.queue) if self.strategy == "bfs" else bool(self.heap)


def audit_case(
    case: AuditCaseSpec,
    registry: FixtureRegistry,
    event_sink: EventSink | None = None,
    strategy: Literal["guided", "bfs"] = "guided",
) -> AuditOutcome:
    """Autonomously explore, falsify claims, minimize, and verify a witness."""
    environment = build_environment(case, registry)
    initial = environment.initial_state()
    _emit(
        event_sink,
        "orient",
        "reset_environment",
        {
            "case_id": case.id,
            "strategy": strategy,
            "initial_state": str(environment.state_key(initial)),
        },
    )
    frontier = SearchFrontier(strategy)
    frontier.push(FrontierNode(state=initial, actions=()), environment.claim_progress(initial))
    seen = {environment.state_key(initial)}
    transitions = 0
    claim_checks = 1
    depth_truncated = False
    state_limit_hit = False
    transition_limit_hit = False

    initial_violation = environment.check_claims(initial)
    if initial_violation is not None:
        witness = _verified_witness(environment, (), 3, event_sink)
        if witness is None:
            outcome = _unstable_finding(case, len(seen), transitions, claim_checks)
        else:
            outcome = _rejection(case, witness, len(seen), transitions, claim_checks)
        _emit(event_sink, "decide", "emit_verdict", {"verdict": outcome.verdict.value})
        return outcome

    while frontier and not transition_limit_hit:
        node = frontier.pop()
        for action in environment.actions(node.state):
            if transitions >= case.max_transitions:
                transition_limit_hit = True
                break
            next_state, observation = environment.step(node.state, action)
            transitions += 1
            next_actions = (*node.actions, action)
            key = environment.state_key(next_state)
            _emit(
                event_sink,
                "explore",
                "execute_action",
                {
                    "depth": len(next_actions),
                    "action": action.display(),
                    "accepted": observation.accepted,
                    "event": observation.event,
                    "state": str(key),
                },
            )
            if len(next_actions) > case.max_depth:
                if key not in seen:
                    depth_truncated = True
                continue

            violation = environment.check_claims(next_state)
            claim_checks += 1
            if violation is not None:
                _emit(
                    event_sink,
                    "explore",
                    "check_claims",
                    {"result": "contradiction", "claim_id": violation.claim_id},
                )
                witness = _verified_witness(environment, next_actions, 3, event_sink)
                if witness is None:
                    outcome = _unstable_finding(case, len(seen), transitions, claim_checks)
                else:
                    outcome = _rejection(case, witness, len(seen), transitions, claim_checks)
                _emit(
                    event_sink,
                    "decide",
                    "emit_verdict",
                    {"verdict": outcome.verdict.value},
                )
                return outcome

            if key in seen:
                continue
            if len(seen) >= case.max_states:
                state_limit_hit = True
                continue
            seen.add(key)
            _emit(
                event_sink,
                "explore",
                "update_coverage_memory",
                {"unique_states": len(seen), "frontier_depth": len(next_actions)},
            )
            progress = environment.claim_progress(next_state)
            frontier.push(FrontierNode(state=next_state, actions=next_actions), progress)
            _emit(
                event_sink,
                "explore",
                "prioritize_frontier",
                {"claim_progress": progress, "strategy": strategy},
            )

    if depth_truncated or state_limit_hit or transition_limit_hit:
        reasons = []
        if depth_truncated:
            reasons.append(f"new reachable states exceeded max_depth={case.max_depth}")
        if state_limit_hit:
            reasons.append(f"state exploration reached max_states={case.max_states}")
        if transition_limit_hit:
            reasons.append(f"transition exploration reached max_transitions={case.max_transitions}")
        outcome = AuditOutcome(
            case_id=case.id,
            verdict=Verdict.UNKNOWN,
            reason="Search incomplete: " + "; ".join(reasons) + ".",
            explored_states=len(seen),
            explored_transitions=transitions,
            claim_checks=claim_checks,
            search_complete=False,
        )
        _emit(event_sink, "decide", "emit_verdict", {"verdict": outcome.verdict.value})
        return outcome

    outcome = AuditOutcome(
        case_id=case.id,
        verdict=Verdict.ACCEPT,
        reason="No contradiction exists in the completely explored finite reachable graph.",
        explored_states=len(seen),
        explored_transitions=transitions,
        claim_checks=claim_checks,
        search_complete=True,
    )
    _emit(event_sink, "decide", "emit_verdict", {"verdict": outcome.verdict.value})
    return outcome


def _verified_witness(
    environment: DeclarativeEnvironment,
    actions: tuple[Action, ...],
    replay_attempts: int,
    event_sink: EventSink | None,
) -> Witness | None:
    minimized = shrink_actions(
        actions,
        lambda candidate: replay_for_violation(environment, candidate) is not None,
    )
    _emit(
        event_sink,
        "verify",
        "shrink_counterexample",
        {"original_length": len(actions), "minimized_length": len(minimized)},
    )
    violations = [replay_for_violation(environment, minimized) for _ in range(replay_attempts)]
    successes = [violation for violation in violations if violation is not None]
    _emit(
        event_sink,
        "verify",
        "replay_counterexample",
        {"attempts": replay_attempts, "successes": len(successes)},
    )
    if len(successes) != replay_attempts:
        return None
    first = successes[0]
    if any(violation != first for violation in successes[1:]):
        return None
    return Witness(
        actions=minimized,
        violation=first,
        replayable=True,
        replay_attempts=replay_attempts,
        replay_successes=len(successes),
        original_length=len(actions),
        minimized_length=len(minimized),
    )


def _unstable_finding(
    case: AuditCaseSpec,
    states: int,
    transitions: int,
    claim_checks: int,
) -> AuditOutcome:
    return AuditOutcome(
        case_id=case.id,
        verdict=Verdict.UNKNOWN,
        reason="A contradiction was observed but did not replay identically three times.",
        explored_states=states,
        explored_transitions=transitions,
        claim_checks=claim_checks,
        search_complete=False,
    )


def _rejection(
    case: AuditCaseSpec,
    witness: Witness,
    states: int,
    transitions: int,
    claim_checks: int,
) -> AuditOutcome:
    return AuditOutcome(
        case_id=case.id,
        verdict=Verdict.REJECT,
        reason=f"Replayable contradiction found for claim {witness.violation.claim_id}.",
        explored_states=states,
        explored_transitions=transitions,
        claim_checks=claim_checks,
        search_complete=False,
        witness=witness,
    )


def _emit(
    event_sink: EventSink | None,
    phase: str,
    tool: str,
    details: dict[str, Primitive],
) -> None:
    if event_sink is not None:
        event_sink.emit(phase, tool, details)
