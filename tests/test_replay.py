from __future__ import annotations

from collections.abc import Sequence

from fidelitygate.environment import build_environment
from fidelitygate.models import Action, SuiteSpec
from fidelitygate.replay import replay_for_violation, shrink_actions


def test_shrinker_removes_irrelevant_actions(suite: SuiteSpec) -> None:
    environment = build_environment(suite.cases[1])
    actions = [
        Action(name="approve_refund", arguments={"role": "operator"}),
        Action(name="submit_refund", arguments={"amount": 1_500}),
        Action(name="issue_refund", arguments={"role": "admin"}),
        Action(name="approve_refund", arguments={"role": "operator"}),
    ]

    def fails(candidate: Sequence[Action]) -> bool:
        return replay_for_violation(environment, candidate) is not None

    minimized = shrink_actions(actions, fails)
    assert [action.name for action in minimized] == ["submit_refund", "issue_refund"]
    assert replay_for_violation(environment, minimized) is not None
    assert not fails(minimized[:1])
    assert not fails(minimized[1:])
