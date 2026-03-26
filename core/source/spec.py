from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceEvidence:
    source: str
    field: str
    value: Any
    confidence: float = 1.0
    detail: str = ""


@dataclass(frozen=True)
class SourceFieldResolution:
    field: str
    value: Any
    status: str
    evidence_sources: tuple[str, ...] = ()
    note: str = ""


@dataclass
class SourceIntent:
    source_type: str | None = None
    fields: dict[str, Any] = field(default_factory=dict)
    evidence: list[SourceEvidence] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    ambiguities: list[str] = field(default_factory=list)
    field_resolutions: dict[str, SourceFieldResolution] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceSpec:
    source_type: str
    fields: dict[str, Any]
    confidence: float = 1.0
    finalization_status: str = "ready"
    field_resolutions: dict[str, SourceFieldResolution] = field(default_factory=dict)
    provenance_summary: dict[str, int] = field(default_factory=dict)
    validation_errors: tuple[str, ...] = field(default_factory=tuple)
    validation_warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def runtime_ready(self) -> bool:
        return self.finalization_status == "ready"
