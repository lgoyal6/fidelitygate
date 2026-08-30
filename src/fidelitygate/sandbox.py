"""Resource-bounded subprocess boundary for the data-only environment interpreter."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

from fidelitygate.models import AuditCaseSpec, AuditOutcome, FixtureRegistry, Verdict

MAX_OUTPUT_BYTES = 2_000_000


def audit_in_sandbox(
    case: AuditCaseSpec,
    registry: FixtureRegistry,
    *,
    timeout_seconds: float = 10.0,
    strategy: Literal["guided", "bfs"] = "guided",
) -> AuditOutcome:
    """Run the deterministic agent in a disposable process with no inherited secrets."""
    request = json.dumps(
        {
            "case": case.model_dump(mode="json"),
            "registry": registry.model_dump(mode="json"),
            "strategy": strategy,
        },
        sort_keys=True,
    )
    environment = {
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": os.environ.get("PATH", ""),
        "PYTHONHASHSEED": "0",
    }
    with tempfile.TemporaryDirectory(prefix="fidelitygate-") as temp_directory:
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-m", "fidelitygate.sandbox_worker"],
                input=request,
                text=True,
                capture_output=True,
                check=False,
                cwd=Path(temp_directory),
                env=environment,
                timeout=timeout_seconds,
                start_new_session=True,
                preexec_fn=_resource_limits if os.name == "posix" else None,
            )
        except subprocess.TimeoutExpired:
            return _sandbox_unknown(case, f"sandbox timed out after {timeout_seconds:.1f}s")
        except OSError as error:
            return _sandbox_unknown(case, f"sandbox could not start: {error}")

    if completed.returncode != 0:
        stderr_text = completed.stderr.strip()[:500]
        return _sandbox_unknown(
            case,
            f"sandbox worker exited with code {completed.returncode}: {stderr_text}",
        )
    encoded = completed.stdout.encode()
    if len(encoded) > MAX_OUTPUT_BYTES:
        return _sandbox_unknown(case, "sandbox output exceeded the 2 MB evidence limit")
    try:
        return AuditOutcome.model_validate_json(completed.stdout)
    except ValueError as error:
        return _sandbox_unknown(case, f"sandbox returned invalid evidence: {error}")


def _resource_limits() -> None:
    """Apply portable POSIX limits before the child interpreter starts."""
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    if sys.platform.startswith("linux"):
        memory = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))


def _sandbox_unknown(case: AuditCaseSpec, reason: str) -> AuditOutcome:
    return AuditOutcome(
        case_id=case.id,
        verdict=Verdict.UNKNOWN,
        reason=reason,
        explored_states=0,
        explored_transitions=0,
        claim_checks=0,
        search_complete=False,
    )
