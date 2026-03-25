from __future__ import annotations

from core.geometry.catalog import get_geometry_catalog_entry
from core.geometry.spec import GeometrySpec


def geometry_spec_to_config_fragment(spec: GeometrySpec) -> dict[str, object]:
    entry = get_geometry_catalog_entry(spec.structure)
    geometry: dict[str, object] = {"structure": spec.structure, "params": {}}
    if entry is None:
        return {"geometry": geometry}

    for param in entry.params:
        value = spec.params.get(param.name)
        if value is None:
            continue
        if param.name.endswith("_triplet_mm") and isinstance(value, list) and len(param.config_param_keys) == 3:
            for key, item in zip(param.config_param_keys, value):
                geometry["params"][key] = float(item)
            geometry[param.name] = [float(item) for item in value]
            continue
        if param.config_param_keys:
            geometry["params"][param.config_param_keys[0]] = float(value)
        geometry[param.name] = int(value) if param.name == "polyhedra_sides" else float(value)

    return {"geometry": geometry}

