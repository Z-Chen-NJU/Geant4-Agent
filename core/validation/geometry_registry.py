from __future__ import annotations

from core.orchestrator.path_ops import flatten, get_path, remove_path
from core.validation.error_codes import E_SCOPE_LEAK


GEOMETRY_FAMILY_REGISTRY: dict[str, dict] = {
    "single_box": {
        "allowed_paths": {
            "geometry.params.module_x",
            "geometry.params.module_y",
            "geometry.params.module_z",
            "geometry.params.tx",
            "geometry.params.ty",
            "geometry.params.tz",
            "geometry.params.rx",
            "geometry.params.ry",
            "geometry.params.rz",
        },
        "required_paths": {
            "geometry.params.module_x",
            "geometry.params.module_y",
            "geometry.params.module_z",
        },
        "name_binding_rules": [{"volume_material_must_match_root": True}],
    },
    "single_tubs": {
        "allowed_paths": {
            "geometry.params.child_rmax",
            "geometry.params.child_hz",
            "geometry.params.tx",
            "geometry.params.ty",
            "geometry.params.tz",
            "geometry.params.rx",
            "geometry.params.ry",
            "geometry.params.rz",
        },
        "required_paths": {"geometry.params.child_rmax", "geometry.params.child_hz"},
        "name_binding_rules": [{"volume_material_must_match_root": True}],
    },
}


def get_geometry_family(structure: str | None) -> dict:
    if not structure:
        return {"allowed_paths": set(), "required_paths": set(), "name_binding_rules": []}
    return GEOMETRY_FAMILY_REGISTRY.get(
        structure,
        {"allowed_paths": set(), "required_paths": set(), "name_binding_rules": []},
    )


def prune_out_of_scope_params(config: dict, family_registry: dict | None = None) -> tuple[dict, list[dict]]:
    registry = family_registry or GEOMETRY_FAMILY_REGISTRY
    structure = str(get_path(config, "geometry.structure", "") or "")
    family = registry.get(structure, {"allowed_paths": set()})
    allowed = set(family.get("allowed_paths", set()))

    params = get_path(config, "geometry.params", {})
    if not isinstance(params, dict):
        return config, []
    flat = flatten({"geometry": {"params": params}})
    errors: list[dict] = []
    for path in flat.keys():
        if path not in allowed:
            remove_path(config, path)
            errors.append(
                {
                    "code": E_SCOPE_LEAK,
                    "path": path,
                    "message": f"param not allowed for structure={structure}",
                }
            )
    return config, errors
