"""M1–M4 metamodels with explicit epistemic status and source traceability."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import Any


def identity(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:24]


class Status(StrEnum):
    OBSERVED = "observed"
    DERIVED = "derived"
    CONJECTURED = "conjectured"


class Verdict(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class SourceLocation:
    path: str
    line: int
    end_line: int
    revision: str
    digest: str
    symbol: str = ""


@dataclass
class BehavioralModel:
    report: str
    trigger: str | None = None
    expected: str | None = None
    observed: str | None = None
    invariants: list[str] = field(default_factory=list)
    ambiguities: list[str] = field(default_factory=list)
    status: str = Status.CONJECTURED.value
    provenance: str = "issue_report"


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    kind: str
    location: SourceLocation
    status: str = Status.DERIVED.value
    resolution: str = "syntactic"


@dataclass
class SystemModel:
    revision: str
    sources: dict[str, str]
    symbols: list[SourceLocation]
    relations: list[Relation]
    diagnostics: list[str] = field(default_factory=list)


@dataclass
class Prediction:
    id: str
    description: str
    predicate: str = "source_contains"
    expected: Any = True
    assumptions: list[str] = field(default_factory=list)


@dataclass
class Probe:
    id: str
    hypothesis_id: str
    kind: str
    path: str
    prediction: Prediction
    parameters: dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 1.0
    reliability: float = 0.5
    alternatives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Evidence:
    id: str
    probe_id: str
    location: SourceLocation
    kind: str
    observation: Any
    procedure: dict[str, Any]
    artifact: str
    artifact_digest: str
    status: str = Status.OBSERVED.value


@dataclass
class FaultHypothesis:
    id: str
    locations: list[SourceLocation]
    mechanism: str
    predictions: list[Prediction]
    causal_chain: list[dict[str, Any]] = field(default_factory=list)
    support: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    score: float = 0.0
    assumptions: list[str] = field(default_factory=list)
    status: str = Status.CONJECTURED.value

    @property
    def path(self) -> str:
        return self.locations[0].path

    def validate(self, evidence: dict[str, Evidence]) -> None:
        if not self.locations or not self.mechanism or not self.predictions:
            raise ValueError("A hypothesis requires locations, a mechanism, and predictions")
        for ref in self.support + self.contradictions:
            if ref not in evidence:
                raise ValueError(f"Missing evidence reference: {ref}")
        for edge in self.causal_chain:
            if edge.get("status") not in {s.value for s in Status}:
                raise ValueError("Every causal edge requires an epistemic status")


@dataclass(frozen=True)
class Assessment:
    hypothesis_id: str
    evidence_id: str
    verdict: str
    scope: str
    reason: str


@dataclass
class Budget:
    tokens: int = 16000
    probes: int = 48
    seconds: float = 3600.0
    input_tokens: int = 0
    output_tokens: int = 0
    probes_used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.tokens - self.input_tokens - self.output_tokens)

    def charge(self, input_tokens: int, output_tokens: int) -> None:
        if min(input_tokens, output_tokens) < 0 or input_tokens + output_tokens > self.remaining:
            raise ValueError("Invalid or over-budget inference charge")
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens


def serialize(value: Any) -> Any:
    return asdict(value)
