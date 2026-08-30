from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from fidelitygate.models import FixtureRegistry, SuiteSpec, Verdict
from fidelitygate.sandbox import audit_in_sandbox


def test_sandbox_reproduces_clean_and_mutated_outcomes(
    suite: SuiteSpec, registry: FixtureRegistry
) -> None:
    clean = audit_in_sandbox(suite.cases[0].audit_input(), registry)
    mutated = audit_in_sandbox(suite.cases[1].audit_input(), registry)

    assert clean.verdict == Verdict.ACCEPT
    assert mutated.verdict == Verdict.REJECT
    assert mutated.witness is not None
    assert mutated.witness.replay_successes == 3


def test_sandbox_timeout_fails_closed(
    suite: SuiteSpec, registry: FixtureRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    def timeout(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        del args, kwargs
        raise subprocess.TimeoutExpired(cmd="fixture", timeout=0.01)

    monkeypatch.setattr(subprocess, "run", timeout)
    outcome = audit_in_sandbox(suite.cases[0].audit_input(), registry, timeout_seconds=0.01)

    assert outcome.verdict == Verdict.UNKNOWN
    assert "timed out" in outcome.reason


def test_data_only_action_name_cannot_execute_shell(
    tmp_path: Path, suite: SuiteSpec, registry: FixtureRegistry
) -> None:
    case = suite.cases[0].audit_input()
    fixture = registry.fixtures[case.fixture_id].model_copy(deep=True)
    target = tmp_path / "should-not-exist"
    fixture.actions[0] = fixture.actions[0].model_copy(update={"name": f"$(touch {target})"})
    fixture.rules[0].action = fixture.actions[0]
    modified = registry.model_copy(deep=True)
    modified.fixtures[case.fixture_id] = fixture

    outcome = audit_in_sandbox(case, modified)

    assert outcome.verdict in {Verdict.ACCEPT, Verdict.REJECT, Verdict.UNKNOWN}
    assert not target.exists()


def test_sandbox_worker_error_and_invalid_output_fail_closed(
    suite: SuiteSpec, registry: FixtureRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = suite.cases[0].audit_input()

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args, returncode=9, stdout="", stderr="worker failed"
        ),
    )
    crashed = audit_in_sandbox(case, registry)
    assert crashed.verdict == Verdict.UNKNOWN
    assert "code 9" in crashed.reason

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args, returncode=0, stdout="not-json", stderr=""
        ),
    )
    invalid = audit_in_sandbox(case, registry)
    assert invalid.verdict == Verdict.UNKNOWN
    assert "invalid evidence" in invalid.reason
