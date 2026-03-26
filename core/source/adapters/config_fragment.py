from __future__ import annotations

from core.source.catalog import get_source_catalog_entry
from core.source.spec import SourceSpec


def _vector3_fragment(value: list[float]) -> dict[str, object]:
    return {"type": "vector", "value": [float(value[0]), float(value[1]), float(value[2])]}


def source_spec_to_config_fragment(spec: SourceSpec) -> dict[str, object]:
    entry = get_source_catalog_entry(spec.source_type)
    source: dict[str, object] = {"type": spec.source_type}
    if entry is None:
        return {"source": source}
    for field_def in entry.fields:
        value = spec.fields.get(field_def.name)
        if value is None or not field_def.config_keys:
            continue
        key = field_def.config_keys[0]
        if field_def.name in {"position_mm", "direction_vec"} and isinstance(value, list):
            source[key] = _vector3_fragment(value)
        else:
            source[key] = value
    return {"source": source}
