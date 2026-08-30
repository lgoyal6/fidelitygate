"""Suite loading, label isolation, metric computation, and evaluation."""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Literal

from fidelitygate.baseline import run_random_baseline, run_replay_baseline
from fidelitygate.environment import load_fixture_registry, resolve_registry_path
from fidelitygate.evidence import compile_evidence_index
from fidelitygate.kernel import audit_case
from fidelitygate.models import (
    CaseResult,
    EvaluationReport,
    GroundTruth,
    Metrics,
    SuiteSpec,
    Verdict,
)
from fidelitygate.sandbox import audit_in_sandbox

SystemName = Literal["replay-baseline", "random-baseline", "bfs-ablation", "fidelitygate"]


def load_suite(path: Path) -> tuple[SuiteSpec, str]:
    """Load and strictly validate a suite while hashing its exact bytes."""
    raw = path.read_bytes()
    suite = SuiteSpec.model_validate_json(raw)
    case_ids = [case.id for case in suite.cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("suite case IDs must be unique")
    return suite, hashlib.sha256(raw).hexdigest()


def evaluate_suite(
    path: Path,
    system: SystemName,
    seed: int = 2026,
    *,
    sandboxed: bool = True,
) -> EvaluationReport:
    """Run one system on unlabeled inputs, then join labels only for scoring."""
    suite, suite_digest = load_suite(path)
    evidence_index = compile_evidence_index(path, suite)
    registry_path = resolve_registry_path(path, suite.fixture_registry)
    registry, registry_digest = load_fixture_registry(registry_path)
    results: list[CaseResult] = []

    for case in suite.cases:
        if case.fixture_id not in registry.fixtures:
            raise ValueError(f"case {case.id} references missing fixture {case.fixture_id}")
        audit_input = case.audit_input()
        if system == "replay-baseline":
            outcome = run_replay_baseline(audit_input, registry)
        elif system == "random-baseline":
            outcome = run_random_baseline(audit_input, registry, seed)
        elif system == "bfs-ablation":
            outcome = (
                audit_in_sandbox(audit_input, registry, strategy="bfs")
                if sandboxed
                else audit_case(audit_input, registry, strategy="bfs")
            )
        else:
            outcome = (
                audit_in_sandbox(audit_input, registry)
                if sandboxed
                else audit_case(audit_input, registry)
            )
        results.append(
            CaseResult.model_validate(
                {
                    **outcome.model_dump(mode="python"),
                    "ground_truth": case.ground_truth,
                    "family": case.family,
                    "critical": case.critical,
                }
            )
        )

    return EvaluationReport(
        suite_id=suite.id,
        suite_sha256=suite_digest,
        fixture_registry_sha256=registry_digest,
        evidence_sha256=evidence_index,
        system=system,
        seed=seed,
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
    replay_attempts = sum(witness.replay_attempts for witness in witnesses)
    replay_successes = sum(witness.replay_successes for witness in witnesses)
    replay_success_rate = replay_successes / replay_attempts if replay_attempts else 1.0
    lengths = [witness.minimized_length for witness in witnesses]
    critical_mutants = [result for result in mutated if result.critical]
    critical_recall = None
    if critical_mutants:
        critical_recall = sum(
            result.verdict == Verdict.REJECT for result in critical_mutants
        ) / len(critical_mutants)

    family_results: dict[str, list[CaseResult]] = defaultdict(list)
    for result in mutated:
        family_results[result.family].append(result)
    family_recall = {
        family: sum(result.verdict == Verdict.REJECT for result in members) / len(members)
        for family, members in sorted(family_results.items())
    }

    return Metrics(
        balanced_accuracy=(clean_specificity + mutant_recall) / 2,
        clean_specificity=clean_specificity,
        mutant_recall=mutant_recall,
        critical_mutant_recall=critical_recall,
        unknown_rate=unknown_count / len(results),
        replay_success_rate=replay_success_rate,
        median_witness_length=statistics.median(lengths) if lengths else None,
        clean_total=len(clean),
        mutated_total=len(mutated),
        correct_clean=correct_clean,
        correct_mutated=correct_mutated,
        unknown_count=unknown_count,
        family_recall=family_recall,
    )


def write_report(report: EvaluationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = report.model_dump(mode="json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
