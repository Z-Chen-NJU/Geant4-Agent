from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


def _normalize_string(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _normalize_positive_float(value: Any) -> float | None:
    if isinstance(value, dict) and "value" in value:
        value = value.get("value")
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _normalize_vector3(value: Any) -> list[float] | None:
    if isinstance(value, dict):
        raw = value.get("value")
        if isinstance(raw, (list, tuple)) and len(raw) >= 3:
            value = raw
        elif all(key in value for key in ("x", "y", "z")):
            value = [value["x"], value["y"], value["z"]]
    if not isinstance(value, (list, tuple)) or len(value) < 3:
        return None
    try:
        return [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class SourceFieldDefinition:
    name: str
    slot_fields: tuple[str, ...]
    semantic_keys: tuple[str, ...]
    config_keys: tuple[str, ...]
    required: bool = False
    runtime_keys: tuple[str, ...] = field(default_factory=tuple)
    normalizer: Callable[[Any], Any | None] = _normalize_string
    description: str = ""

    def normalize_value(self, value: Any) -> Any | None:
        return self.normalizer(value)


@dataclass(frozen=True)
class SourceCatalogEntry:
    source_type: str
    kind_aliases: tuple[str, ...]
    fields: tuple[SourceFieldDefinition, ...]
    required_fields: tuple[str, ...]
    ignored_fields: tuple[str, ...] = field(default_factory=tuple)
    supported_in_runtime: bool = True
    description: str = ""


_COMMON_FIELDS = {
    "particle": SourceFieldDefinition(
        name="particle",
        slot_fields=("particle",),
        semantic_keys=("particle",),
        config_keys=("particle",),
        required=True,
        runtime_keys=("particle",),
        description="Particle name.",
    ),
    "energy_mev": SourceFieldDefinition(
        name="energy_mev",
        slot_fields=("energy_mev",),
        semantic_keys=("energy",),
        config_keys=("energy",),
        required=True,
        runtime_keys=("energy",),
        normalizer=_normalize_positive_float,
        description="Source energy in MeV.",
    ),
    "position_mm": SourceFieldDefinition(
        name="position_mm",
        slot_fields=("position_mm",),
        semantic_keys=("position",),
        config_keys=("position",),
        required=True,
        runtime_keys=("position",),
        normalizer=_normalize_vector3,
        description="Source position in mm.",
    ),
    "direction_vec": SourceFieldDefinition(
        name="direction_vec",
        slot_fields=("direction_vec",),
        semantic_keys=("direction",),
        config_keys=("direction",),
        required=False,
        runtime_keys=("direction",),
        normalizer=_normalize_vector3,
        description="Direction vector.",
    ),
}

_SOURCE_CATALOG: tuple[SourceCatalogEntry, ...] = (
    SourceCatalogEntry(
        source_type="point",
        kind_aliases=("point", "point_source"),
        fields=(
            _COMMON_FIELDS["particle"],
            _COMMON_FIELDS["energy_mev"],
            _COMMON_FIELDS["position_mm"],
            _COMMON_FIELDS["direction_vec"],
        ),
        required_fields=("particle", "energy_mev", "position_mm"),
        description="Single point source.",
    ),
    SourceCatalogEntry(
        source_type="beam",
        kind_aliases=("beam", "pencil_beam", "collimated"),
        fields=(
            _COMMON_FIELDS["particle"],
            _COMMON_FIELDS["energy_mev"],
            _COMMON_FIELDS["position_mm"],
            SourceFieldDefinition(
                name="direction_vec",
                slot_fields=("direction_vec",),
                semantic_keys=("direction",),
                config_keys=("direction",),
                required=True,
                runtime_keys=("direction",),
                normalizer=_normalize_vector3,
                description="Required direction vector for beam sources.",
            ),
        ),
        required_fields=("particle", "energy_mev", "position_mm", "direction_vec"),
        description="Directed beam source.",
    ),
    SourceCatalogEntry(
        source_type="isotropic",
        kind_aliases=("isotropic",),
        fields=(
            _COMMON_FIELDS["particle"],
            _COMMON_FIELDS["energy_mev"],
            _COMMON_FIELDS["position_mm"],
            _COMMON_FIELDS["direction_vec"],
        ),
        required_fields=("particle", "energy_mev", "position_mm"),
        ignored_fields=("direction_vec",),
        supported_in_runtime=False,
        description="Isotropic source centered at a position.",
    ),
    SourceCatalogEntry(
        source_type="plane",
        kind_aliases=("plane", "plane_source"),
        fields=(
            _COMMON_FIELDS["particle"],
            _COMMON_FIELDS["energy_mev"],
            _COMMON_FIELDS["position_mm"],
            _COMMON_FIELDS["direction_vec"],
        ),
        required_fields=("particle", "energy_mev", "position_mm", "direction_vec"),
        supported_in_runtime=False,
        description="Plane source placeholder for future runtime expansion.",
    ),
)

_ALIASES: dict[str, str] = {}
for entry in _SOURCE_CATALOG:
    _ALIASES[entry.source_type] = entry.source_type
    for alias in entry.kind_aliases:
        _ALIASES[alias] = entry.source_type


def resolve_source_type(value: Any) -> str | None:
    key = str(value or "").strip().lower()
    return _ALIASES.get(key)


def get_source_catalog_entry(source_type: Any) -> SourceCatalogEntry | None:
    resolved = resolve_source_type(source_type)
    if resolved is None:
        return None
    for entry in _SOURCE_CATALOG:
        if entry.source_type == resolved:
            return entry
    return None


def iter_source_catalog() -> tuple[SourceCatalogEntry, ...]:
    return _SOURCE_CATALOG
