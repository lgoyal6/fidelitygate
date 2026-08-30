"""Typed contracts shared by the harness, adapters, and reports."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Primitive = str | int | float | bool | None


class StrictModel(BaseModel):
    """Forbid silent manifest/schema drift."""

    model_config = ConfigDict(extra="forbid")


class Verdict(StrEnum):
    """Bounded decision returned by an auditing system."""

    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class GroundTruth(StrEnum):
    """Benchmark label held in the suite manifest."""

    CLEAN = "clean"
    MUTATED = "mutated"


class Action(StrictModel):
    """A schema-validated action supplied to an environment adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    arguments: dict[str, Primitive] = Field(default_factory=dict)

    def display(self) -> str:
        """Return a stable compact representation for reports."""
        if not self.arguments:
            return self.name
        args = ", ".join(f"{key}={self.arguments[key]!r}" for key in sorted(self.arguments))
        return f"{self.name}({args})"


class ClaimSpec(StrictModel):
    """A machine-checkable claim plus its evidence provenance."""

    id: str
    statement: str
    source: str
    severity: Literal["low", "medium", "high", "critical"]


class CaseSpec(StrictModel):
    """One versioned environment case."""

    id: str
    adapter: Literal["refund"]
    ground_truth: GroundTruth
    mutation: Literal["none", "admin_approval_bypass"]
    max_depth: Annotated[int, Field(ge=1, le=20)]
    max_states: Annotated[int, Field(ge=1, le=100_000)] = 10_000
    expert_traces: list[list[Action]]
    claims: list[ClaimSpec]


class SuiteSpec(StrictModel):
    """Evaluation suite loaded identically by every system."""

    schema_version: Literal["1"]
    id: str
    description: str
    cases: list[CaseSpec]


class Observation(StrictModel):
    """Normalized result of an environment transition."""

    accepted: bool
    event: str
    details: dict[str, Primitive] = Field(default_factory=dict)


class ClaimViolation(StrictModel):
    """Observed contradiction of a declared claim."""

    claim_id: str
    statement: str
    source: str
    expected: str
    observed: str


class Witness(StrictModel):
    """A minimized counterexample with replay evidence."""

    actions: list[Action]
    violation: ClaimViolation
    replayable: bool
    original_length: Annotated[int, Field(ge=0)]
    minimized_length: Annotated[int, Field(ge=0)]


class CaseResult(StrictModel):
    """Auditor output for one case."""

    case_id: str
    ground_truth: GroundTruth
    verdict: Verdict
    reason: str
    explored_states: Annotated[int, Field(ge=0)]
    explored_transitions: Annotated[int, Field(ge=0)]
    search_complete: bool
    witness: Witness | None = None


class Metrics(StrictModel):
    """Aggregate metrics with transparent confusion counts."""

    balanced_accuracy: float
    clean_specificity: float
    mutant_recall: float
    unknown_rate: float
    replay_success_rate: float
    median_witness_length: float | None
    clean_total: int
    mutated_total: int
    correct_clean: int
    correct_mutated: int
    unknown_count: int


class EvaluationReport(StrictModel):
    """Machine-readable output of a system on a frozen suite."""

    schema_version: Literal["1"] = "1"
    suite_id: str
    suite_sha256: str
    system: Literal["replay-baseline", "fidelitygate"]
    results: list[CaseResult]
    metrics: Metrics
