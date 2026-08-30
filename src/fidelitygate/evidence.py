"""Compile source-backed claims into a validated, hashed evidence index."""

from __future__ import annotations

import hashlib
from pathlib import Path

from fidelitygate.models import SuiteSpec


def compile_evidence_index(suite_path: Path, suite: SuiteSpec) -> dict[str, str]:
    """Validate every source, anchor, and exact excerpt before evaluation."""
    repository_root = suite_path.resolve().parents[2]
    evidence_root = (repository_root / "evidence").resolve()
    hashes: dict[str, str] = {}
    for case in suite.cases:
        for claim in case.claims:
            source_path_text, separator, anchor = claim.source.partition("#")
            if not separator or not anchor:
                raise ValueError(f"claim {claim.id} source must include a fragment anchor")
            source_path = (repository_root / source_path_text).resolve()
            if not source_path.is_relative_to(evidence_root):
                raise ValueError(f"claim {claim.id} source must stay inside evidence/")
            if not source_path.is_file():
                raise FileNotFoundError(source_path)
            content = source_path.read_text(encoding="utf-8")
            if f'<a id="{anchor}"></a>' not in content:
                raise ValueError(f"claim {claim.id} source anchor does not exist: {anchor}")
            if claim.source_excerpt not in content:
                raise ValueError(f"claim {claim.id} excerpt does not occur in its source")
            relative = str(source_path.relative_to(repository_root))
            hashes[relative] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    return dict(sorted(hashes.items()))
