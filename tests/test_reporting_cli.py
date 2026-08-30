from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

from fidelitygate.cli import app
from fidelitygate.evaluation import evaluate_suite
from fidelitygate.html_report import write_html_report
from fidelitygate.reporting import print_report, write_comparison


def test_reports_render_complete_comparison(tmp_path: Path, suite_path: Path) -> None:
    reports = [
        evaluate_suite(suite_path, "replay-baseline", sandboxed=False),
        evaluate_suite(suite_path, "random-baseline", sandboxed=False),
        evaluate_suite(suite_path, "fidelitygate", sandboxed=False),
    ]
    output = tmp_path / "comparison.md"
    write_comparison(reports, output)
    rendered = output.read_text(encoding="utf-8")

    assert "Replay baseline" in rendered
    assert "Random baseline" in rendered
    assert "FidelityGate" in rendered
    assert "env_001a" in rendered
    assert "evidence/policies/synthetic-policies.md" in rendered

    stream = StringIO()
    print_report(reports[-1], Console(file=stream, width=160))
    assert "balanced_accuracy=1.000" in stream.getvalue()

    html_path = tmp_path / "report.html"
    write_html_report(reports, html_path)
    html = html_path.read_text(encoding="utf-8")
    assert "FidelityGate evidence memo" in html
    assert "Replayable contradictions" in html
    assert "3/3 identical" in html


def test_comparison_rejects_incompatible_inputs(suite_path: Path, tmp_path: Path) -> None:
    report = evaluate_suite(suite_path, "fidelitygate", sandboxed=False)
    with pytest.raises(ValueError, match="at least two"):
        write_comparison([report], tmp_path / "invalid.md")

    changed = report.model_copy(update={"suite_id": "different"})
    with pytest.raises(ValueError, match="identical suite"):
        write_comparison([report, changed], tmp_path / "invalid.md")


def test_cli_eval_and_compare(tmp_path: Path, suite_path: Path) -> None:
    runner = CliRunner()
    report_path = tmp_path / "report.json"
    evaluation = runner.invoke(
        app,
        [
            "eval",
            "--suite",
            str(suite_path),
            "--system",
            "fidelitygate",
            "--output",
            str(report_path),
        ],
    )
    assert evaluation.exit_code == 0, evaluation.output
    assert report_path.is_file()
    assert "balanced_accuracy=1.000" in evaluation.output

    comparison_dir = tmp_path / "comparison"
    comparison = runner.invoke(
        app,
        [
            "compare",
            "--suite",
            str(suite_path),
            "--output",
            str(comparison_dir),
        ],
    )
    assert comparison.exit_code == 0, comparison.output
    assert (comparison_dir / "comparison.md").is_file()
    assert (comparison_dir / "report.html").is_file()
    assert (comparison_dir / "random-baseline.json").is_file()

    trajectory_path = tmp_path / "trajectory.json"
    trajectory = runner.invoke(
        app,
        [
            "trace",
            "--suite",
            str(suite_path),
            "--case-id",
            "env_001b",
            "--output",
            str(trajectory_path),
        ],
    )
    assert trajectory.exit_code == 0, trajectory.output
    assert trajectory_path.is_file()
    assert "verdict=REJECT" in trajectory.output


def test_cli_trace_rejects_unknown_case(tmp_path: Path, suite_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "trace",
            "--suite",
            str(suite_path),
            "--case-id",
            "missing",
            "--output",
            str(tmp_path / "missing.json"),
        ],
    )
    assert result.exit_code != 0
    assert "case not found" in result.output
