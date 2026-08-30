"""Action replay and counterexample minimization."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

from fidelitygate.environment import EnvironmentAdapter
from fidelitygate.models import Action, ClaimViolation

StateT = TypeVar("StateT")


def replay_for_violation(
    environment: EnvironmentAdapter[StateT], actions: Sequence[Action]
) -> ClaimViolation | None:
    """Replay from reset and return the first claim contradiction."""
    state = environment.initial_state()
    initial_violation = environment.check_claims(state)
    if initial_violation is not None:
        return initial_violation

    for action in actions:
        state, _ = environment.step(state, action)
        violation = environment.check_claims(state)
        if violation is not None:
            return violation
    return None


def shrink_actions(
    actions: Sequence[Action], fails: Callable[[Sequence[Action]], bool]
) -> list[Action]:
    """Greedily delete actions until every remaining single deletion heals the failure."""
    candidate = list(actions)
    changed = True
    while changed:
        changed = False
        for index in range(len(candidate)):
            trial = candidate[:index] + candidate[index + 1 :]
            if fails(trial):
                candidate = trial
                changed = True
                break
    return candidate
