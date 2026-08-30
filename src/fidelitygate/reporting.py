"""Judge-facing terminal and Markdown reports."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from fidelitygate.models import EvaluationReport


def print_report(report: EvaluationReport, console: Console | None = None) -> None:
    """Render metrics and per-case verdicts without hiding failures."""
    console = console or Console()
    table = Table(title=f"{report.system} on {report.suite_id}")
    table.add_column("Case")
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


def write_comparison(baseline: EvaluationReport, final: EvaluationReport, path: Path) -> None:
    """Write the primary measured improvement as Markdown."""
    path.parent.mkdir(parents=True, exist_ok=True)
    delta = final.metrics.balanced_accuracy - baseline.metrics.balanced_accuracy
    baseline_row = _metric_row("Replay baseline", baseline)
    final_row = _metric_row("FidelityGate", final)
    change_row = " | ".join(
        [
            "| Change",
            f"{delta:+.3f}",
            f"{final.metrics.clean_specificity - baseline.metrics.clean_specificity:+.3f}",
            f"{final.metrics.mutant_recall - baseline.metrics.mutant_recall:+.3f}",
            f"{final.metrics.unknown_rate - baseline.metrics.unknown_rate:+.3f}",
            (f"{final.metrics.replay_success_rate - baseline.metrics.replay_success_rate:+.3f}"),
            "|",
        ]
    )
    content = "\n".join(
        [
            "# Smoke evaluation comparison",
            "",
            f"Suite: `{baseline.suite_id}`",
            f"Suite SHA-256: `{baseline.suite_sha256}`",
            "",
            (
                "| System | Balanced accuracy | Clean specificity | Mutant recall | "
                "Unknown rate | Replay success |"
            ),
            "|---|---:|---:|---:|---:|---:|",
            baseline_row,
            final_row,
            change_row,
            "",
            "## Claim boundary",
            "",
            (
                "This two-case smoke suite demonstrates the causal failure of replay-only "
                "validation on one approval-bypass mutant and verifies the end-to-end harness. "
                "It does not estimate general detector performance."
            ),
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def _metric_row(label: str, report: EvaluationReport) -> str:
    metrics = report.metrics
    return " | ".join(
        [
            f"| {label}",
            f"{metrics.balanced_accuracy:.3f}",
            f"{metrics.clean_specificity:.3f}",
            f"{metrics.mutant_recall:.3f}",
            f"{metrics.unknown_rate:.3f}",
            f"{metrics.replay_success_rate:.3f}",
            "|",
        ]
    )
