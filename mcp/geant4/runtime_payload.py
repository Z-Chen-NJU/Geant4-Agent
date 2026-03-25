from __future__ import annotations

from copy import deepcopy
from typing import Any


def _coerce_vector3(value: Any, fallback: list[float]) -> list[float]:
    if isinstance(value, dict):
        if isinstance(value.get("value"), list) and len(value["value"]) >= 3:
            try:
                return [float(value["value"][0]), float(value["value"][1]), float(value["value"][2])]
            except (TypeError, ValueError):
                return list(fallback)
        keys = ("x", "y", "z")
        if all(key in value for key in keys):
            try:
                return [float(value["x"]), float(value["y"]), float(value["z"])]
            except (TypeError, ValueError):
                return list(fallback)
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        try:
            return [float(value[0]), float(value[1]), float(value[2])]
        except (TypeError, ValueError):
            return list(fallback)
    return list(fallback)


def _first_material(config: dict[str, Any]) -> str:
    materials = config.get("materials", {}) if isinstance(config.get("materials"), dict) else {}
    vmap = materials.get("volume_material_map")
    if isinstance(vmap, dict):
        for _, material in vmap.items():
            if material:
                return str(material)
    if isinstance(vmap, list):
        for item in vmap:
            if isinstance(item, dict) and item.get("material"):
                return str(item["material"])
    selected = materials.get("selected_materials")
    if isinstance(selected, list):
        for item in selected:
            if item:
                return str(item)
    return "G4_Cu"


def _physics_list_name(config: dict[str, Any]) -> str:
    physics_list = config.get("physics_list")
    if isinstance(physics_list, dict) and physics_list.get("name"):
        return str(physics_list["name"])
    physics = config.get("physics")
    if isinstance(physics, dict) and physics.get("physics_list"):
        return str(physics["physics_list"])
    if isinstance(physics_list, str) and physics_list.strip():
        return physics_list.strip()
    return "FTFP_BERT"


def build_runtime_payload(config: dict[str, Any]) -> dict[str, Any]:
    raw = deepcopy(config) if isinstance(config, dict) else {}

    geometry = raw.get("geometry", {}) if isinstance(raw.get("geometry"), dict) else {}
    params = geometry.get("params", {}) if isinstance(geometry.get("params"), dict) else {}
    source = raw.get("source", {}) if isinstance(raw.get("source"), dict) else {}
    structure = str(geometry.get("structure") or "single_box")

    position = _coerce_vector3(source.get("position"), [0.0, 0.0, -100.0])
    direction = _coerce_vector3(source.get("direction"), [0.0, 0.0, 1.0])

    payload = {
        "structure": structure,
        "material": _first_material(raw),
        "particle": str(source.get("particle") or "gamma"),
        "source_type": str(source.get("type") or "point"),
        "physics_list": _physics_list_name(raw),
        "energy": float(source.get("energy") or 1.0),
        "position": {"x": position[0], "y": position[1], "z": position[2]},
        "direction": {"x": direction[0], "y": direction[1], "z": direction[2]},
        "raw_config": raw,
    }

    if structure == "single_tubs":
        payload["radius"] = float(params.get("child_rmax") or geometry.get("radius_mm") or 25.0)
        payload["half_length"] = float(params.get("child_hz") or geometry.get("half_length_mm") or 50.0)
    else:
        size_triplet = geometry.get("size_triplet_mm")
        if isinstance(size_triplet, (list, tuple)) and len(size_triplet) >= 3:
            payload["size_x"] = float(size_triplet[0])
            payload["size_y"] = float(size_triplet[1])
            payload["size_z"] = float(size_triplet[2])
        else:
            payload["size_x"] = float(params.get("module_x") or 50.0)
            payload["size_y"] = float(params.get("module_y") or 50.0)
            payload["size_z"] = float(params.get("module_z") or 50.0)

    return payload
