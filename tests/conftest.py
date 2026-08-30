from __future__ import annotations

from pathlib import Path

import pytest

from fidelitygate.environment import load_fixture_registry, resolve_registry_path
from fidelitygate.models import FixtureRegistry, SuiteSpec


@pytest.fixture
def suite_path() -> Path:
    return Path(__file__).parents[1] / "evals" / "suites" / "smoke.json"


@pytest.fixture
def suite(suite_path: Path) -> SuiteSpec:
    return SuiteSpec.model_validate_json(suite_path.read_bytes())


@pytest.fixture
def registry(suite_path: Path, suite: SuiteSpec) -> FixtureRegistry:
    path = resolve_registry_path(suite_path, suite.fixture_registry)
    registry, _ = load_fixture_registry(path)
    return registry
