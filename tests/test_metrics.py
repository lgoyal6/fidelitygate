from __future__ import annotations

from fidelitygate.evaluation import compute_metrics
from fidelitygate.models import CaseResult, GroundTruth, Verdict


def result(case_id: str, truth: GroundTruth, verdict: Verdict) -> CaseResult:
    return CaseResult(
        case_id=case_id,
        ground_truth=truth,
        verdict=verdict,
        reason="fixture",
        explored_states=0,
        explored_transitions=0,
        claim_checks=0,
        search_complete=verdict != Verdict.UNKNOWN,
        family="fixture-family",
        critical=False,
    )


def test_unknown_counts_incorrect_for_its_class() -> None:
    metrics = compute_metrics(
        [
            result("clean-a", GroundTruth.CLEAN, Verdict.ACCEPT),
            result("clean-b", GroundTruth.CLEAN, Verdict.UNKNOWN),
            result("mutant-a", GroundTruth.MUTATED, Verdict.REJECT),
            result("mutant-b", GroundTruth.MUTATED, Verdict.UNKNOWN),
        ]
    )

    assert metrics.clean_specificity == 0.5
    assert metrics.mutant_recall == 0.5
    assert metrics.balanced_accuracy == 0.5
    assert metrics.unknown_rate == 0.5
