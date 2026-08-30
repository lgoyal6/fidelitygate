"""Minimal stdin/stdout protocol for the FidelityGate subprocess boundary."""

from __future__ import annotations

import json
import sys

from fidelitygate.kernel import audit_case
from fidelitygate.models import AuditCaseSpec, FixtureRegistry


def main() -> None:
    request = json.loads(sys.stdin.read())
    if not isinstance(request, dict):
        raise ValueError("sandbox request must be an object")
    case = AuditCaseSpec.model_validate(request.get("case"))
    registry = FixtureRegistry.model_validate(request.get("registry"))
    strategy = request.get("strategy", "guided")
    if strategy not in {"guided", "bfs"}:
        raise ValueError("unknown search strategy")
    outcome = audit_case(case, registry, strategy=strategy)
    sys.stdout.write(outcome.model_dump_json())


if __name__ == "__main__":
    main()
