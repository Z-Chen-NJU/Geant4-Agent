from __future__ import annotations

from dataclasses import dataclass, field

from core.domain.geometry import GEOMETRY_KIND_TO_STRUCTURE
from core.domain.geometry_family import GEOMETRY_FAMILY_REGISTRY


@dataclass(frozen=True)
class GeometryParamDefinition:
    name: str
    slot_fields: tuple[str, ...]
    required: bool = False
    unit: str = "mm"
    description: str = ""


@dataclass(frozen=True)
class GeometryCatalogEntry:
    structure: str
    kind_aliases: tuple[str, ...]
    required_slot_fields: tuple[str, ...]
    params: tuple[GeometryParamDefinition, ...]
    allowed_paths: frozenset[str] = field(default_factory=frozenset)
    required_paths: frozenset[str] = field(default_factory=frozenset)


_CATALOG: dict[str, GeometryCatalogEntry] = {
    "single_box": GeometryCatalogEntry(
        structure="single_box",
        kind_aliases=("box", "cube", "single_box"),
        required_slot_fields=("kind", "size_triplet_mm"),
        params=(
            GeometryParamDefinition(
                name="size_triplet_mm",
                slot_fields=("size_triplet_mm",),
                required=True,
                description="Full edge lengths along x/y/z in millimetres.",
            ),
        ),
        allowed_paths=frozenset(GEOMETRY_FAMILY_REGISTRY["single_box"]["allowed_paths"]),
        required_paths=frozenset(GEOMETRY_FAMILY_REGISTRY["single_box"]["required_paths"]),
    ),
    "single_tubs": GeometryCatalogEntry(
        structure="single_tubs",
        kind_aliases=("cylinder", "tubs", "single_tubs"),
        required_slot_fields=("kind", "radius_mm", "half_length_mm"),
        params=(
            GeometryParamDefinition(
                name="radius_mm",
                slot_fields=("radius_mm",),
                required=True,
                description="Outer radius in millimetres.",
            ),
            GeometryParamDefinition(
                name="half_length_mm",
                slot_fields=("half_length_mm",),
                required=True,
                description="Half length along z in millimetres.",
            ),
        ),
        allowed_paths=frozenset(GEOMETRY_FAMILY_REGISTRY["single_tubs"]["allowed_paths"]),
        required_paths=frozenset(GEOMETRY_FAMILY_REGISTRY["single_tubs"]["required_paths"]),
    ),
}


def resolve_geometry_structure(kind_or_structure: str | None) -> str | None:
    text = str(kind_or_structure or "").strip().lower()
    if not text:
        return None
    if text in _CATALOG:
        return text
    mapped = GEOMETRY_KIND_TO_STRUCTURE.get(text)
    if mapped in _CATALOG:
        return mapped
    for structure, entry in _CATALOG.items():
        if text in entry.kind_aliases:
            return structure
    return None


def get_geometry_catalog_entry(structure: str | None) -> GeometryCatalogEntry | None:
    resolved = resolve_geometry_structure(structure)
    if not resolved:
        return None
    return _CATALOG.get(resolved)

