from __future__ import annotations

import pytest

from fidelitygate.environment import build_environment
from fidelitygate.models import Action, FixtureRegistry, SuiteSpec


def test_clean_environment_denies_high_value_issue_without_approval(
    suite: SuiteSpec, registry: FixtureRegistry
) -> None:
    environment = build_environment(suite.cases[0].audit_input(), registry)
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


def test_mutant_allows_and_exposes_admin_bypass(
    suite: SuiteSpec, registry: FixtureRegistry
) -> None:
    environment = build_environment(suite.cases[1].audit_input(), registry)
    state = environment.initial_state()
    state, _ = environment.step(state, Action(name="submit_refund", arguments={"amount": 1_500}))
    state, issued = environment.step(
        state, Action(name="issue_refund", arguments={"role": "admin"})
    )

    violation = environment.check_claims(state)
    assert issued.accepted is True
    assert violation is not None
    assert violation.claim_id == "refund.high_value_approval"


def test_expert_traces_pass_in_clean_and_mutated_environments(
    suite: SuiteSpec, registry: FixtureRegistry
) -> None:
    for case in suite.cases:
        environment = build_environment(case.audit_input(), registry)
        for trace in case.expert_traces:
            state = environment.initial_state()
            for selected_action in trace:
                state, observation = environment.step(state, selected_action)
                assert observation.accepted is True
                assert environment.check_claims(state) is None


def test_audit_input_excludes_ground_truth(suite: SuiteSpec) -> None:
    public_fields = suite.cases[0].audit_input().model_dump()
    assert "ground_truth" not in public_fields
    assert "family" not in public_fields
    assert "critical" not in public_fields


def test_fixture_rejects_unknown_state_field(suite: SuiteSpec, registry: FixtureRegistry) -> None:
    case = suite.cases[0].audit_input()
    malformed = registry.fixtures[case.fixture_id].model_copy(deep=True)
    malformed.rules[0].requires[0].field = "not_a_state_field"
    bad_registry = registry.model_copy(deep=True)
    bad_registry.fixtures[case.fixture_id] = malformed

    with pytest.raises(ValueError, match="unknown field"):
        build_environment(case, bad_registry)
