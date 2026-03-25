from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GeometryEvidence:
    source: str
    field: str
    value: Any
    confidence: float = 1.0


@dataclass
class GeometryIntent:
    structure: str | None = None
    kind: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    evidence: list[GeometryEvidence] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    ambiguities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GeometrySpec:
    structure: str
    params: dict[str, float | list[float]]
    allowed_paths: frozenset[str] = field(default_factory=frozenset)
    required_paths: frozenset[str] = field(default_factory=frozenset)

