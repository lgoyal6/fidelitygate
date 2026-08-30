from __future__ import annotations

from fidelitygate.baseline import run_random_baseline, run_replay_baseline
from fidelitygate.models import Action, FixtureRegistry, SuiteSpec, Verdict


def test_replay_baseline_rejects_an_invalid_expert_trace(
    suite: SuiteSpec, registry: FixtureRegistry
) -> None:
    case = suite.cases[0].audit_input().model_copy(deep=True)
    case.expert_traces = [[Action(name="issue_refund", arguments={"role": "admin"})]]

    outcome = run_replay_baseline(case, registry)

    assert outcome.verdict == Verdict.REJECT
    assert "failed at action" in outcome.reason


def test_budgeted_random_baseline_finds_mutant_but_abstains_on_clean(
    suite: SuiteSpec, registry: FixtureRegistry
) -> None:
    clean = run_random_baseline(suite.cases[0].audit_input(), registry, seed=2026)
    mutated = run_random_baseline(suite.cases[1].audit_input(), registry, seed=2026)

    assert clean.verdict == Verdict.UNKNOWN
    assert mutated.verdict == Verdict.REJECT
    assert mutated.witness is not None
    assert mutated.witness.replayable is True
