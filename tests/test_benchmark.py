from __future__ import annotations

import re
from pathlib import Path

from fidelitygate.benchmark import build_benchmark, write_benchmark
from fidelitygate.environment import build_environment
from fidelitygate.kernel import audit_case
from fidelitygate.models import Action, GroundTruth
from fidelitygate.replay import replay_for_violation, replay_trace


def test_full_benchmark_has_fourteen_balanced_pairs() -> None:
    registry, full, smoke, mutations = build_benchmark()

    assert len(full.cases) == 28
    assert len(registry.fixtures) == 28
    assert len(mutations) == 14
    assert len(smoke.cases) == 2
    assert sum(case.ground_truth == GroundTruth.CLEAN for case in full.cases) == 14
    assert sum(case.ground_truth == GroundTruth.MUTATED for case in full.cases) == 14
    assert len({case.family for case in full.cases}) == 14
    assert all(re.fullmatch(r"wf_\d{3}[ab]", case.fixture_id) for case in full.cases)


def test_generated_benchmark_artifacts_are_current() -> None:
    root = Path(__file__).resolve().parents[1]
    write_benchmark(root, check=True)

    development = (root / "evals" / "suites" / "envmutationbench-dev.json").read_text()
    holdout = (root / "evals" / "suites" / "envmutationbench-holdout.json").read_text()
    assert development.count('"ground_truth":') == 20
    assert holdout.count('"ground_truth":') == 8


def test_claim_excerpts_exist_in_synthetic_policy() -> None:
    root = Path(__file__).resolve().parents[1]
    policy = (root / "evidence" / "policies" / "synthetic-policies.md").read_text(encoding="utf-8")
    _, full, _, _ = build_benchmark()

    for case in full.cases:
        for selected_claim in case.claims:
            assert selected_claim.source_excerpt in policy


def test_every_mutation_is_discriminating_and_expert_invisible() -> None:
    registry, full, _, mutations = build_benchmark()
    cases_by_fixture = {case.fixture_id: case for case in full.cases}

    for mutation in mutations:
        clean_case = cases_by_fixture[str(mutation["clean_fixture_id"])]
        mutant_case = cases_by_fixture[str(mutation["mutated_fixture_id"])]
        clean_environment = build_environment(clean_case.audit_input(), registry)
        mutant_environment = build_environment(mutant_case.audit_input(), registry)
        raw_trigger = mutation["minimal_trigger"]
        assert isinstance(raw_trigger, list)
        minimal_trigger = [Action.model_validate(item) for item in raw_trigger]

        assert replay_for_violation(clean_environment, minimal_trigger) is None
        assert replay_for_violation(mutant_environment, minimal_trigger) is not None
        for expert_trace in clean_case.expert_traces:
            assert replay_trace(clean_environment, expert_trace) == (True, None)
            assert replay_trace(mutant_environment, expert_trace) == (True, None)


def test_full_auditor_accepts_every_clean_and_rejects_every_mutant() -> None:
    registry, full, _, _ = build_benchmark()

    for case in full.cases:
        outcome = audit_case(case.audit_input(), registry)
        expected = "ACCEPT" if case.ground_truth == GroundTruth.CLEAN else "REJECT"
        assert outcome.verdict.value == expected
