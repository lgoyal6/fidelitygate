from __future__ import annotations

import pytest
from pydantic import ValidationError

from fidelitygate.models import SuiteSpec


def test_manifest_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        SuiteSpec.model_validate(
            {
                "schema_version": "1",
                "id": "invalid",
                "description": "fixture",
                "cases": [],
                "silently_ignored": True,
            }
        )
