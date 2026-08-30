"""Product-agent trajectory recording with a stable public schema."""

from __future__ import annotations

import json
from pathlib import Path

from fidelitygate.models import AgentEvent, AgentTrajectory, AuditOutcome, Primitive

AGENT_INSTRUCTION = (
    "Try to falsify every source-backed environment claim within the declared bounds. "
    "Use only the unlabeled case, action interface, observations, coverage memory, claim "
    "checker, shrinker, and replay tool. Reject only for a contradiction that replays "
    "identically three times; accept only after the finite reachable graph is complete; "
    "otherwise return UNKNOWN."
)


class TrajectoryRecorder:
    """Append-only in-memory event sink for one representative audit."""

    def __init__(self) -> None:
        self.events: list[AgentEvent] = []

    def emit(
        self,
        phase: str,
        tool: str,
        details: dict[str, Primitive],
    ) -> None:
        self.events.append(
            AgentEvent.model_validate(
                {
                    "sequence": len(self.events) + 1,
                    "phase": phase,
                    "tool": tool,
                    "details": details,
                }
            )
        )

    def package(self, case_id: str, outcome: AuditOutcome) -> AgentTrajectory:
        return AgentTrajectory(
            agent="fidelitygate-falsification-agent",
            instruction=AGENT_INSTRUCTION,
            case_id=case_id,
            events=self.events,
            outcome=outcome,
        )


def write_agent_trajectory(trajectory: AgentTrajectory, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(trajectory.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
