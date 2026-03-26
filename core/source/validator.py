from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

from core.source.catalog import SourceCatalogEntry
from core.source.spec import SourceIntent


@dataclass(frozen=True)
class SourceValidationResult:
    status: str
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    provenance_summary: dict[str, int] = field(default_factory=dict)


def _vector_norm(value: list[float]) -> float:
    return sqrt(sum(float(item) * float(item) for item in value))


def validate_source_intent(intent: SourceIntent, entry: SourceCatalogEntry) -> SourceValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    provenance_summary: dict[str, int] = {}

    for resolution in intent.field_resolutions.values():
        provenance_summary[resolution.status] = provenance_summary.get(resolution.status, 0) + 1
        if resolution.status == "ambiguous":
            warnings.append(f"ambiguous_field:{resolution.field}")

    particle = intent.fields.get("particle")
    if not isinstance(particle, str) or not particle.strip():
        errors.append("invalid_particle")
    energy = intent.fields.get("energy_mev")
    if energy is not None and float(energy) <= 0:
        errors.append("non_positive_energy")
    position = intent.fields.get("position_mm")
    if position is not None:
        if not isinstance(position, list) or len(position) != 3:
            errors.append("invalid_position")
    direction = intent.fields.get("direction_vec")
    if direction is not None:
        if not isinstance(direction, list) or len(direction) != 3:
            errors.append("invalid_direction")
        elif _vector_norm(direction) == 0:
            errors.append("zero_direction")

    if intent.source_type == "beam" and direction is None:
        errors.append("beam_requires_direction")
    if intent.source_type in {"isotropic", "plane"} and direction is not None:
        warnings.append(f"direction_ignored_for_{intent.source_type}")
    if not entry.supported_in_runtime:
        warnings.append(f"runtime_not_supported:{entry.source_type}")

    status = "ready"
    if errors:
        status = "invalid"
    elif intent.ambiguities or warnings:
        status = "review"
    return SourceValidationResult(
        status=status,
        errors=tuple(sorted(set(errors))),
        warnings=tuple(sorted(set(warnings))),
        provenance_summary=provenance_summary,
    )
