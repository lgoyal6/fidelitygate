"""Evidence-first terminal and Markdown reports."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from fidelitygate.models import EvaluationReport


def print_report(report: EvaluationReport, console: Console | None = None) -> None:
    console = console or Console()
    table = Table(title=f"{report.system} on {report.suite_id}")
    table.add_column("Case")
    table.add_column("Family")
    table.add_column("Truth")
    table.add_column("Verdict")
    table.add_column("States", justify="right")
    table.add_column("Transitions", justify="right")
    table.add_column("Witness")
    for result in report.results:
        witness = "—"
        if result.witness is not None:
            witness = " → ".join(action.display() for action in result.witness.actions)
        table.add_row(
            result.case_id,
            result.family,
            result.ground_truth.value,
            result.verdict.value,
            str(result.explored_states),
            str(result.explored_transitions),
            witness,
        )
    console.print(table)
    metrics = report.metrics
    console.print(
        f"balanced_accuracy={metrics.balanced_accuracy:.3f}  "
        f"clean_specificity={metrics.clean_specificity:.3f}  "
        f"mutant_recall={metrics.mutant_recall:.3f}  "
        f"unknown_rate={metrics.unknown_rate:.3f}"
    )


def write_comparison(reports: list[EvaluationReport], path: Path) -> None:
    """Write complete comparable outcomes without omitting baseline failures."""
    if len(reports) < 2:
        raise ValueError("comparison requires at least two reports")
    suite_ids = {report.suite_id for report in reports}
    suite_hashes = {report.suite_sha256 for report in reports}
    registry_hashes = {report.fixture_registry_sha256 for report in reports}
    evidence_hashes = {tuple(sorted(report.evidence_sha256.items())) for report in reports}
    if (
        len(suite_ids) != 1
        or len(suite_hashes) != 1
        or len(registry_hashes) != 1
        or len(evidence_hashes) != 1
    ):
        raise ValueError("comparison reports must use identical suite and fixture bytes")

    path.parent.mkdir(parents=True, exist_ok=True)
    baseline = reports[0]
    rows = [_metric_row(_system_label(report.system), report) for report in reports]
    content = "\n".join(
        [
            "# Evaluation comparison",
            "",
            f"Suite: `{baseline.suite_id}`",
            f"Suite SHA-256: `{baseline.suite_sha256}`",
            f"Fixture registry SHA-256: `{baseline.fixture_registry_sha256}`",
            "Evidence SHA-256:",
            *[f"- `{source}`: `{digest}`" for source, digest in baseline.evidence_sha256.items()],
            f"Seed: `{baseline.seed}`",
            "",
            (
                "| System | Balanced accuracy | Clean specificity | Mutant recall | "
                "Critical recall | Unknown rate | Replay success |"
            ),
            "|---|---:|---:|---:|---:|---:|---:|",
            *rows,
            "",
            "## Per-case outcomes",
            "",
            _per_case_table(reports),
            "",
            "## Claim boundary",
            "",
            (
                "The smoke suite verifies a causal implementation path only. The full benchmark "
                "covers multiple paired mutation families, but it remains synthetic and does not "
                "by itself establish performance on proprietary production environments."
            ),
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def _system_label(system: str) -> str:
    return {
        "replay-baseline": "Replay baseline",
        "random-baseline": "Random baseline",
        "bfs-ablation": "BFS ablation",
        "fidelitygate": "FidelityGate",
    }.get(system, system)


def _metric_row(label: str, report: EvaluationReport) -> str:
    metrics = report.metrics
    critical = (
        "n/a" if metrics.critical_mutant_recall is None else f"{metrics.critical_mutant_recall:.3f}"
    )
    return " | ".join(
        [
            f"| {label}",
            f"{metrics.balanced_accuracy:.3f}",
            f"{metrics.clean_specificity:.3f}",
            f"{metrics.mutant_recall:.3f}",
            critical,
            f"{metrics.unknown_rate:.3f}",
            f"{metrics.replay_success_rate:.3f}",
            "|",
        ]
    )


def _per_case_table(reports: list[EvaluationReport]) -> str:
    header = (
        "| Case | Family | Truth | "
        + " | ".join(_system_label(report.system) for report in reports)
        + " |"
    )
    separator = "|---|---|---|" + "---|" * len(reports)
    result_maps = [{result.case_id: result for result in report.results} for report in reports]
    lines = [header, separator]
    for reference in reports[0].results:
        verdicts = " | ".join(results[reference.case_id].verdict.value for results in result_maps)
        lines.append(
            f"| {reference.case_id} | {reference.family} | "
            f"{reference.ground_truth.value} | {verdicts} |"
        )
    return "\n".join(lines)
