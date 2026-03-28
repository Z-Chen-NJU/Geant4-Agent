from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceSpan:
    text: str
    role: str


@dataclass
class TurnSummary:
    intent: str = "other"
    focus: str = "mixed"
    scope: str = "partial_update"
    user_goal: str = ""
    explicit_domains: list[str] = field(default_factory=list)
    uncertain_domains: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GeometryCandidate:
    kind_candidate: str | None = None
    material_candidate: str | None = None
    dimension_hints: dict[str, Any] = field(default_factory=dict)
    placement_relation: str | None = None
    confidence: float = 0.0
    ambiguities: list[str] = field(default_factory=list)
    evidence_spans: list[EvidenceSpan] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_spans"] = [asdict(span) for span in self.evidence_spans]
        return payload


@dataclass
class SourceCandidate:
    source_type_candidate: str | None = None
    particle_candidate: str | None = None
    energy_candidate_mev: float | None = None
    position_mode: str | None = None
    position_hint: dict[str, Any] = field(default_factory=dict)
    direction_mode: str | None = None
    direction_hint: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    ambiguities: list[str] = field(default_factory=list)
    evidence_spans: list[EvidenceSpan] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_spans"] = [asdict(span) for span in self.evidence_spans]
        return payload
