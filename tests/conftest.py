from __future__ import annotations

from pathlib import Path

import pytest

from fidelitygate.models import SuiteSpec


@pytest.fixture
def suite_path() -> Path:
    return Path(__file__).parents[1] / "evals" / "suites" / "smoke.json"


@pytest.fixture
def suite(suite_path: Path) -> SuiteSpec:
    return SuiteSpec.model_validate_json(suite_path.read_bytes())
