"""Command-line interface for reproducible evaluations."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer

from fidelitygate.environment import load_fixture_registry, resolve_registry_path
from fidelitygate.evaluation import evaluate_suite, load_suite, write_report
from fidelitygate.evidence import compile_evidence_index
from fidelitygate.html_report import write_html_report
from fidelitygate.kernel import audit_case
from fidelitygate.reporting import print_report, write_comparison
from fidelitygate.trajectory import TrajectoryRecorder, write_agent_trajectory

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command("eval")
def evaluate_command(
    suite: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    system: Annotated[
        Literal["replay-baseline", "random-baseline", "bfs-ablation", "fidelitygate"],
        typer.Option(),
    ],
    output: Annotated[Path | None, typer.Option(dir_okay=False)] = None,
    seed: Annotated[int, typer.Option()] = 2026,
) -> None:
    """Evaluate one system on a frozen suite."""
    report = evaluate_suite(suite, system, seed)
    if output is not None:
        write_report(report, output)
    print_report(report)


@app.command("compare")
def compare_command(
    suite: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    output: Annotated[Path, typer.Option(file_okay=False)] = Path("artifacts/smoke"),
    seed: Annotated[int, typer.Option()] = 2026,
) -> None:
    """Run the baseline and FidelityGate on identical cases and compare them."""
    baseline = evaluate_suite(suite, "replay-baseline", seed)
    random_baseline = evaluate_suite(suite, "random-baseline", seed)
    bfs_ablation = evaluate_suite(suite, "bfs-ablation", seed)
    final = evaluate_suite(suite, "fidelitygate", seed)
    output.mkdir(parents=True, exist_ok=True)
    write_report(baseline, output / "baseline.json")
    write_report(random_baseline, output / "random-baseline.json")
    write_report(bfs_ablation, output / "bfs-ablation.json")
    write_report(final, output / "fidelitygate.json")
    write_comparison([baseline, random_baseline, bfs_ablation, final], output / "comparison.md")
    write_html_report([baseline, random_baseline, bfs_ablation, final], output / "report.html")
    print_report(baseline)
    print_report(random_baseline)
    print_report(bfs_ablation)
    print_report(final)
    typer.echo(f"Wrote comparison artifacts to {output}")


@app.command("trace")
def trace_command(
    suite: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    case_id: Annotated[str, typer.Option()],
    output: Annotated[Path, typer.Option(dir_okay=False)],
) -> None:
    """Export a judge-readable trajectory for one product-agent execution."""
    suite_spec, _ = load_suite(suite)
    compile_evidence_index(suite, suite_spec)
    registry_path = resolve_registry_path(suite, suite_spec.fixture_registry)
    registry, _ = load_fixture_registry(registry_path)
    try:
        selected_case = next(case for case in suite_spec.cases if case.id == case_id)
    except StopIteration as error:
        raise typer.BadParameter(f"case not found in suite: {case_id}") from error
    recorder = TrajectoryRecorder()
    outcome = audit_case(selected_case.audit_input(), registry, recorder)
    trajectory = recorder.package(selected_case.id, outcome)
    write_agent_trajectory(trajectory, output)
    typer.echo(
        f"Wrote {len(trajectory.events)} events for {case_id}; verdict={outcome.verdict.value}"
    )


if __name__ == "__main__":
    app()
