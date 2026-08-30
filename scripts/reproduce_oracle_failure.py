#!/usr/bin/env python3
"""Reproduce the first benchmark-oracle failure instead of hiding it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fidelitygate.benchmark import build_benchmark, condition
from fidelitygate.evaluation import compute_metrics
from fidelitygate.kernel import audit_case
from fidelitygate.models import CaseResult


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/iterations/oracle-failure.json"),
    )
    args = parser.parse_args()
    registry, suite, _, _ = build_benchmark()
    flawed_suite = suite.model_copy(deep=True)
    flawed_registry = registry.model_copy(deep=True)

    temporal_clean = flawed_suite.cases[6]
    temporal_clean.claims[0].forbidden_when = [
        condition("accessed", True),
        condition("expired", True),
    ]

    tenant_clean = flawed_suite.cases[16]
    tenant_fixture = flawed_registry.fixtures[tenant_clean.fixture_id]
    for selected_rule in tenant_fixture.rules:
        if selected_rule.action.name == "verify_identity":
            selected_rule.requires = [
                requirement
                for requirement in selected_rule.requires
                if requirement.field != "reset"
            ]

    results: list[CaseResult] = []
    for case in flawed_suite.cases:
        outcome = audit_case(case.audit_input(), flawed_registry, strategy="bfs")
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
    metrics = compute_metrics(results)
    clean_failures = [
        result.model_dump(mode="json")
        for result in results
        if result.ground_truth.value == "clean" and result.verdict.value != "ACCEPT"
    ]
    payload: dict[str, object] = {
        "experiment": "iteration-1-flawed-benchmark-oracles",
        "changes_reproduced": [
            "Temporal claim encoded final-state co-occurrence instead of access-after-expiry.",
            "Recovery verification remained enabled after the terminal reset transition.",
        ],
        "metrics": metrics.model_dump(mode="json"),
        "clean_failures": clean_failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        f"Reproduced balanced_accuracy={metrics.balanced_accuracy:.3f} "
        f"with {len(clean_failures)} clean-case failures."
    )


if __name__ == "__main__":
    main()
