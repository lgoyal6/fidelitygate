from __future__ import annotations

from pathlib import Path

import pytest

from fidelitygate.evaluation import load_suite
from fidelitygate.evidence import compile_evidence_index


def test_evidence_compiler_hashes_verified_sources(suite_path: Path) -> None:
    suite, _ = load_suite(suite_path)
    index = compile_evidence_index(suite_path, suite)

    assert set(index) == {"evidence/policies/synthetic-policies.md"}
    assert len(next(iter(index.values()))) == 64


def test_evidence_compiler_rejects_forged_excerpt(suite_path: Path) -> None:
    suite, _ = load_suite(suite_path)
    suite = suite.model_copy(deep=True)
    suite.cases[0].claims[0].source_excerpt = "This sentence was not approved."

    with pytest.raises(ValueError, match="excerpt does not occur"):
        compile_evidence_index(suite_path, suite)


def test_evidence_compiler_rejects_path_escape(suite_path: Path) -> None:
    suite, _ = load_suite(suite_path)
    suite = suite.model_copy(deep=True)
    suite.cases[0].claims[0].source = "../pyproject.toml#project"

    with pytest.raises(ValueError, match="inside evidence"):
        compile_evidence_index(suite_path, suite)
