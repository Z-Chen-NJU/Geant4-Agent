from __future__ import annotations

from dataclasses import dataclass, field

from core.geometry.catalog import GeometryCatalogEntry
from core.geometry.spec import GeometryIntent


@dataclass(frozen=True)
class GeometryValidationResult:
    status: str
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    provenance_summary: dict[str, int] = field(default_factory=dict)


def validate_geometry_intent(intent: GeometryIntent, entry: GeometryCatalogEntry) -> GeometryValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    provenance_summary: dict[str, int] = {}

    for resolution in intent.field_resolutions.values():
        provenance_summary[resolution.status] = provenance_summary.get(resolution.status, 0) + 1
        if resolution.status == "ambiguous":
            warnings.append(f"ambiguous_field:{resolution.field}")

    for param in entry.params:
        value = intent.params.get(param.name)
        if value is None:
            continue
        if param.value_kind == "triplet":
            if not isinstance(value, list) or len(value) != param.arity:
                errors.append(f"invalid_triplet:{param.name}")
                continue
            if any(float(item) <= 0 for item in value):
                errors.append(f"non_positive_triplet:{param.name}")
            continue
        if param.value_kind == "integer":
            if int(value) <= 0:
                errors.append(f"non_positive_integer:{param.name}")
            continue
        if float(value) <= 0:
            errors.append(f"non_positive_scalar:{param.name}")

    status = "ready"
    if errors:
        status = "invalid"
    elif intent.ambiguities or warnings:
        status = "ambiguous"
    return GeometryValidationResult(
        status=status,
        errors=tuple(sorted(set(errors))),
        warnings=tuple(sorted(set(warnings))),
        provenance_summary=provenance_summary,
    )
