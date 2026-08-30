"""Suite loading, metric computation, and system evaluation."""

from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Literal

from fidelitygate.baseline import run_replay_baseline
from fidelitygate.kernel import audit_case
from fidelitygate.models import (
    CaseResult,
    EvaluationReport,
    GroundTruth,
    Metrics,
    SuiteSpec,
    Verdict,
)

SystemName = Literal["replay-baseline", "fidelitygate"]


def load_suite(path: Path) -> tuple[SuiteSpec, str]:
    """Load and strictly validate a suite while hashing its exact bytes."""
    raw = path.read_bytes()
    suite = SuiteSpec.model_validate_json(raw)
    return suite, hashlib.sha256(raw).hexdigest()


def evaluate_suite(path: Path, system: SystemName) -> EvaluationReport:
    """Run one system on every case in a frozen suite."""
    suite, digest = load_suite(path)
    runner = run_replay_baseline if system == "replay-baseline" else audit_case
    results = [runner(case) for case in suite.cases]
    return EvaluationReport(
        suite_id=suite.id,
        suite_sha256=digest,
        system=system,
        results=results,
        metrics=compute_metrics(results),
    )


def compute_metrics(results: list[CaseResult]) -> Metrics:
    """Compute the frozen metric contract; UNKNOWN is always incorrect."""
    clean = [result for result in results if result.ground_truth == GroundTruth.CLEAN]
    mutated = [result for result in results if result.ground_truth == GroundTruth.MUTATED]
    if not clean or not mutated:
        raise ValueError("evaluation requires at least one clean and one mutated case")

    correct_clean = sum(result.verdict == Verdict.ACCEPT for result in clean)
    correct_mutated = sum(result.verdict == Verdict.REJECT for result in mutated)
    clean_specificity = correct_clean / len(clean)
    mutant_recall = correct_mutated / len(mutated)
    unknown_count = sum(result.verdict == Verdict.UNKNOWN for result in results)
    witnesses = [result.witness for result in results if result.witness is not None]
    replay_successes = sum(witness.replayable for witness in witnesses)
    replay_success_rate = replay_successes / len(witnesses) if witnesses else 1.0
    lengths = [witness.minimized_length for witness in witnesses]

    return Metrics(
        balanced_accuracy=(clean_specificity + mutant_recall) / 2,
        clean_specificity=clean_specificity,
        mutant_recall=mutant_recall,
        unknown_rate=unknown_count / len(results),
        replay_success_rate=replay_success_rate,
        median_witness_length=statistics.median(lengths) if lengths else None,
        clean_total=len(clean),
        mutated_total=len(mutated),
        correct_clean=correct_clean,
        correct_mutated=correct_mutated,
        unknown_count=unknown_count,
    )


def write_report(report: EvaluationReport, path: Path) -> None:
    """Write a stable, human-diffable JSON artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = report.model_dump(mode="json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
