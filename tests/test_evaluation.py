from __future__ import annotations

from pathlib import Path

from fidelitygate.evaluation import evaluate_suite, load_suite
from fidelitygate.kernel import audit_case
from fidelitygate.models import Verdict


def test_replay_baseline_misses_mutant(suite_path: Path) -> None:
    report = evaluate_suite(suite_path, "replay-baseline")

    assert report.metrics.balanced_accuracy == 0.5
    assert report.metrics.clean_specificity == 1.0
    assert report.metrics.mutant_recall == 0.0
    assert [result.verdict for result in report.results] == [
        Verdict.ACCEPT,
        Verdict.ACCEPT,
    ]


def test_fidelitygate_separates_clean_and_mutated_pair(suite_path: Path) -> None:
    report = evaluate_suite(suite_path, "fidelitygate")

    assert report.metrics.balanced_accuracy == 1.0
    assert report.metrics.clean_specificity == 1.0
    assert report.metrics.mutant_recall == 1.0
    clean, mutant = report.results
    assert clean.verdict == Verdict.ACCEPT
    assert clean.search_complete is True
    assert mutant.verdict == Verdict.REJECT
    assert mutant.witness is not None
    assert mutant.witness.replayable is True
    assert mutant.witness.minimized_length == 2
    assert [action.display() for action in mutant.witness.actions] == [
        "submit_refund(amount=1500)",
        "issue_refund(role='admin')",
    ]


def test_fidelitygate_returns_unknown_when_depth_bound_is_incomplete(suite_path: Path) -> None:
    report = evaluate_suite(suite_path, "fidelitygate")
    mutant_case = report.results[1]
    assert mutant_case.verdict == Verdict.REJECT

    suite, _ = load_suite(suite_path)
    truncated = suite.cases[1].model_copy(update={"max_depth": 1})
    result = audit_case(truncated)

    assert result.verdict == Verdict.UNKNOWN
    assert result.search_complete is False
    assert "max_depth=1" in result.reason
