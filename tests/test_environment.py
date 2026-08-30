from __future__ import annotations

from fidelitygate.environment import build_environment
from fidelitygate.models import Action, SuiteSpec


def test_clean_environment_denies_high_value_issue_without_approval(suite: SuiteSpec) -> None:
    environment = build_environment(suite.cases[0])
    state = environment.initial_state()
    state, submitted = environment.step(
        state, Action(name="submit_refund", arguments={"amount": 1_500})
    )
    state, issued = environment.step(
        state, Action(name="issue_refund", arguments={"role": "admin"})
    )

    assert submitted.accepted is True
    assert issued.accepted is False
    assert environment.check_claims(state) is None


def test_mutant_allows_and_exposes_admin_bypass(suite: SuiteSpec) -> None:
    environment = build_environment(suite.cases[1])
    state = environment.initial_state()
    state, _ = environment.step(state, Action(name="submit_refund", arguments={"amount": 1_500}))
    state, issued = environment.step(
        state, Action(name="issue_refund", arguments={"role": "admin"})
    )

    violation = environment.check_claims(state)
    assert issued.accepted is True
    assert violation is not None
    assert violation.claim_id == "refund.high_value_approval"


def test_expert_traces_pass_in_clean_and_mutated_environments(suite: SuiteSpec) -> None:
    for case in suite.cases:
        environment = build_environment(case)
        for trace in case.expert_traces:
            state = environment.initial_state()
            for action in trace:
                state, observation = environment.step(state, action)
                assert observation.accepted is True
                assert environment.check_claims(state) is None
