# ruff: noqa: E501
"""Self-contained evidence memo suitable for review and printing."""

from __future__ import annotations

from html import escape
from pathlib import Path

from fidelitygate.models import EvaluationReport, Verdict


def write_html_report(reports: list[EvaluationReport], path: Path) -> None:
    if not reports:
        raise ValueError("HTML report requires at least one evaluation report")
    final = reports[-1]
    findings = [result for result in final.results if result.verdict == Verdict.REJECT]
    unknowns = [result for result in final.results if result.verdict == Verdict.UNKNOWN]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _document(reports, findings_count=len(findings), unknown_count=len(unknowns)),
        encoding="utf-8",
    )


def _document(reports: list[EvaluationReport], *, findings_count: int, unknown_count: int) -> str:
    final = reports[-1]
    metrics = final.metrics
    status = "Review required" if findings_count else "No contradiction found within bounds"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FidelityGate evidence memo — {escape(final.suite_id)}</title>
<style>
:root{{--ink:#172033;--muted:#5d687a;--paper:#fff;--wash:#f4f6f9;--line:#d9dee8;--red:#a52828;--green:#176b45;--amber:#8a5a00;--blue:#3157c8}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--wash);color:var(--ink);font:15px/1.5 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:1120px;margin:32px auto;background:var(--paper);padding:48px;box-shadow:0 8px 30px #17203312}}
h1{{font-size:32px;line-height:1.15;margin:0 0 8px}} h2{{margin-top:38px;border-bottom:1px solid var(--line);padding-bottom:8px}} h3{{margin-bottom:6px}}
.eyebrow{{color:var(--blue);font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:12px}} .muted{{color:var(--muted)}}
.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}} .metric{{border:1px solid var(--line);padding:16px;border-radius:8px}}
.metric strong{{display:block;font-size:25px}} table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{border-bottom:1px solid var(--line);text-align:left;padding:9px 8px;vertical-align:top}} th{{background:var(--wash)}}
.ACCEPT{{color:var(--green);font-weight:700}} .REJECT{{color:var(--red);font-weight:700}} .UNKNOWN{{color:var(--amber);font-weight:700}}
.finding{{border-left:4px solid var(--red);padding:4px 18px;margin:22px 0}} code{{background:var(--wash);padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}} ol{{padding-left:24px}}
.boundary{{border:1px solid var(--line);background:var(--wash);padding:16px;border-radius:8px}} .hash{{font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere}}
@media(max-width:760px){{main{{margin:0;padding:24px}}.summary{{grid-template-columns:1fr 1fr}}}} @media print{{body{{background:white}}main{{box-shadow:none;margin:0;max-width:none}}}}
</style>
</head>
<body><main>
<div class="eyebrow">Evidence-bounded environment acceptance</div>
<h1>FidelityGate evidence memo</h1>
<p class="muted">Suite <code>{escape(final.suite_id)}</code> · deterministic seed {final.seed}</p>
<h2>{escape(status)}</h2>
<p>The final agent found {findings_count} replayable contradiction(s) and returned UNKNOWN for {unknown_count} case(s). A qualified reviewer remains the approval authority.</p>
<section class="summary">
{_metric("Balanced accuracy", metrics.balanced_accuracy)}
{_metric("Clean specificity", metrics.clean_specificity)}
{_metric("Mutant recall", metrics.mutant_recall)}
{_metric("Replay success", metrics.replay_success_rate)}
</section>
<h2>System comparison</h2>
{_comparison_table(reports)}
<h2>Complete case results</h2>
{_case_table(reports)}
<h2>Replayable contradictions</h2>
{_findings(final)}
<h2>Uncertainty</h2>
{_unknowns(final)}
<h2>Provenance</h2>
<p class="hash">Suite SHA-256: {escape(final.suite_sha256)}<br>Fixture registry SHA-256: {escape(final.fixture_registry_sha256)}</p>
{_evidence_hashes(final)}
<h2>Decision boundary</h2>
<div class="boundary">REJECT means a source-backed contradiction replayed identically three times. ACCEPT means the finite reachable graph was complete within the declared model and bounds. UNKNOWN means search, evidence, execution, or replay was incomplete. Synthetic benchmark performance does not establish production-environment performance.</div>
</main></body></html>
"""


def _metric(label: str, value: float) -> str:
    return f'<div class="metric"><span>{escape(label)}</span><strong>{value:.3f}</strong></div>'


def _comparison_table(reports: list[EvaluationReport]) -> str:
    rows = []
    for report in reports:
        metrics = report.metrics
        rows.append(
            "<tr>"
            f"<td>{escape(report.system)}</td>"
            f"<td>{metrics.balanced_accuracy:.3f}</td>"
            f"<td>{metrics.clean_specificity:.3f}</td>"
            f"<td>{metrics.mutant_recall:.3f}</td>"
            f"<td>{metrics.unknown_rate:.3f}</td>"
            f"<td>{metrics.replay_success_rate:.3f}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>System</th><th>Balanced accuracy</th>"
        "<th>Clean specificity</th><th>Mutant recall</th><th>Unknown rate</th>"
        "<th>Replay success</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def _case_table(reports: list[EvaluationReport]) -> str:
    maps = [{result.case_id: result for result in report.results} for report in reports]
    headers = "".join(f"<th>{escape(report.system)}</th>" for report in reports)
    rows = []
    for reference in reports[0].results:
        verdicts = "".join(
            f'<td class="{result_map[reference.case_id].verdict.value}">'
            f"{result_map[reference.case_id].verdict.value}</td>"
            for result_map in maps
        )
        rows.append(
            f"<tr><td>{escape(reference.case_id)}</td><td>{escape(reference.family)}</td>"
            f"<td>{escape(reference.ground_truth.value)}</td>{verdicts}</tr>"
        )
    return (
        f"<table><thead><tr><th>Case</th><th>Family</th><th>Truth</th>{headers}</tr>"
        "</thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def _findings(report: EvaluationReport) -> str:
    sections = []
    for result in report.results:
        if result.verdict != Verdict.REJECT or result.witness is None:
            continue
        witness = result.witness
        steps = "".join(
            f"<li><code>{escape(action.display())}</code></li>" for action in witness.actions
        )
        sections.append(
            f'<article class="finding"><h3>{escape(result.case_id)} · '
            f"{escape(witness.violation.claim_id)}</h3>"
            f"<p><strong>Source:</strong> <code>{escape(witness.violation.source)}</code><br>"
            f"<strong>Approved excerpt:</strong> “{escape(witness.violation.source_excerpt)}”</p>"
            f"<ol>{steps}</ol><p><strong>Observed:</strong> "
            f"{escape(witness.violation.observed)}</p>"
            f"<p>Replay: {witness.replay_successes}/{witness.replay_attempts} identical · "
            f"witness length {witness.minimized_length}</p></article>"
        )
    return "".join(sections) or "<p>No replayable contradiction was reported.</p>"


def _unknowns(report: EvaluationReport) -> str:
    items = [
        f"<li><code>{escape(result.case_id)}</code>: {escape(result.reason)}</li>"
        for result in report.results
        if result.verdict == Verdict.UNKNOWN
    ]
    return f"<ul>{''.join(items)}</ul>" if items else "<p>No case returned UNKNOWN.</p>"


def _evidence_hashes(report: EvaluationReport) -> str:
    items = "".join(
        f'<li><code>{escape(source)}</code>: <span class="hash">{escape(digest)}</span></li>'
        for source, digest in report.evidence_sha256.items()
    )
    return f"<p>Evidence files:</p><ul>{items}</ul>"
