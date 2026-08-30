"""Command-line interface for reproducible evaluations."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer

from fidelitygate.evaluation import evaluate_suite, write_report
from fidelitygate.reporting import print_report, write_comparison

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command("eval")
def evaluate_command(
    suite: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    system: Annotated[Literal["replay-baseline", "fidelitygate"], typer.Option()],
    output: Annotated[Path | None, typer.Option(dir_okay=False)] = None,
) -> None:
    """Evaluate one system on a frozen suite."""
    report = evaluate_suite(suite, system)
    if output is not None:
        write_report(report, output)
    print_report(report)


@app.command("compare")
def compare_command(
    suite: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    output: Annotated[Path, typer.Option(file_okay=False)] = Path("artifacts/smoke"),
) -> None:
    """Run the baseline and FidelityGate on identical cases and compare them."""
    baseline = evaluate_suite(suite, "replay-baseline")
    final = evaluate_suite(suite, "fidelitygate")
    output.mkdir(parents=True, exist_ok=True)
    write_report(baseline, output / "baseline.json")
    write_report(final, output / "fidelitygate.json")
    write_comparison(baseline, final, output / "comparison.md")
    print_report(baseline)
    print_report(final)
    typer.echo(f"Wrote comparison artifacts to {output}")


if __name__ == "__main__":
    app()
