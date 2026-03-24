from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from builder.geometry.synthesize import synthesize_from_params


ROOT = Path(__file__).parent
SCHEMA_PATH = ROOT.parent.parent / "core" / "schema" / "geant4_min_config.schema.json"


def apply_frame(
    config: Dict[str, Any],
    frame: Any,
    debug: Dict[str, Any],
    autofix: bool,
    geometry_hint: Optional[str],
) -> Dict[str, Any]:
    structure = frame.geometry.structure
    if not structure and geometry_hint:
        structure = geometry_hint
    if structure:
        config["geometry"]["structure"] = structure
    if getattr(frame.geometry, "chosen_skeleton", None):
        config["geometry"]["chosen_skeleton"] = frame.geometry.chosen_skeleton
    if frame.geometry.params:
        config["geometry"]["params"].update(frame.geometry.params)
    if getattr(frame.geometry, "graph_program", None):
        config["geometry"]["graph_program"] = frame.geometry.graph_program

    if config["geometry"].get("graph_program"):
        config["geometry"]["dsl"] = config["geometry"]["graph_program"]
        chosen = debug.get("graph_chosen_skeleton", "")
        gcands = debug.get("graph_candidates", [])
        cobj = None
        for candidate in gcands:
            if candidate.get("structure") == chosen:
                cobj = candidate
                break
        if cobj is not None:
            config["geometry"]["feasible"] = bool(cobj.get("feasible", False))
            config["geometry"]["errors"] = list(cobj.get("errors", []))
            config["geometry"]["warnings"] = list(cobj.get("warnings", []))
            config["geometry"]["missing_params"] = list(cobj.get("missing_params", []))
        else:
            config["geometry"]["feasible"] = None
            config["geometry"]["errors"] = []
            config["geometry"]["warnings"] = []
            config["geometry"]["missing_params"] = []
        config["geometry"]["scores"] = debug.get("scores", {})
        config["geometry"]["ranked"] = debug.get("ranked", [])
    elif config["geometry"]["structure"]:
        synth = synthesize_from_params(
            config["geometry"]["structure"],
            config["geometry"]["params"],
            seed=7,
            apply_autofix=autofix,
        )
        config["geometry"]["dsl"] = synth.get("dsl")
        config["geometry"]["feasible"] = synth.get("feasible")
        config["geometry"]["errors"] = synth.get("errors", [])
        config["geometry"]["missing_params"] = synth.get("missing_params", [])
        config["geometry"]["scores"] = debug.get("scores", {})
        config["geometry"]["ranked"] = debug.get("ranked", [])
    else:
        config["geometry"]["dsl"] = None
        config["geometry"]["feasible"] = None
        config["geometry"]["errors"] = ["structure confidence below threshold"]
        config["geometry"]["missing_params"] = []
        config["geometry"]["scores"] = debug.get("scores", {})
        config["geometry"]["ranked"] = debug.get("ranked", [])

    for mat in frame.materials.selected_materials:
        if mat not in config["materials"]["selected_materials"]:
            config["materials"]["selected_materials"].append(mat)
    if frame.physics.physics_list:
        config["physics"]["physics_list"] = frame.physics.physics_list
    if frame.source.particle:
        config["source"]["particle"] = frame.source.particle
    if frame.source.type:
        config["source"]["type"] = frame.source.type
    if frame.output.format:
        config["output"]["format"] = frame.output.format
    config["notes"].extend(getattr(frame, "notes", []))
    return config


def _parse_source_energy_mev(text: str) -> Optional[float]:
    match = re.search(r"([-+]?\d*\.?\d+)\s*(mev|gev|kev)", text.lower())
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2)
    if unit == "gev":
        return value * 1000.0
    if unit == "kev":
        return value * 0.001
    return value


def _parse_triplet(text: str, key: str) -> Optional[Dict[str, Any]]:
    pattern = rf"{key}\s*[:=]?\s*\(?\s*([-+]?\d*\.?\d+)\s*[, ]\s*([-+]?\d*\.?\d+)\s*[, ]\s*([-+]?\d*\.?\d+)\s*\)?"
    match = re.search(pattern, text.lower())
    if not match:
        return None
    return {"type": "vector", "value": [float(match.group(1)), float(match.group(2)), float(match.group(3))]}


def _infer_direction_from_text(text: str) -> Optional[Dict[str, Any]]:
    low = text.lower().replace(" ", "")
    mapping = [
        (("+z", "沿+z", "towards+z", "along+z"), [0.0, 0.0, 1.0]),
        (("-z", "沿-z", "towards-z", "along-z"), [0.0, 0.0, -1.0]),
        (("+x", "沿+x", "towards+x", "along+x"), [1.0, 0.0, 0.0]),
        (("-x", "沿-x", "towards-x", "along-x"), [-1.0, 0.0, 0.0]),
        (("+y", "沿+y", "towards+y", "along+y"), [0.0, 1.0, 0.0]),
        (("-y", "沿-y", "towards-y", "along-y"), [0.0, -1.0, 0.0]),
    ]
    for keys, vec in mapping:
        if any(key in low for key in keys):
            return {"type": "vector", "value": vec}
    return None


def _infer_position_from_text(text: str) -> Optional[Dict[str, Any]]:
    low = text.lower()
    if any(key in low for key in ["origin", "at origin", "原点", "中心", "center"]):
        return {"type": "vector", "value": [0.0, 0.0, 0.0]}
    return None


def _parse_output_path(text: str) -> Optional[str]:
    match = re.search(r"([A-Za-z]:[\\/][^\s]+\.(?:root|csv|json|xml|hdf5|h5)|[./\\\w-]+\.(?:root|csv|json|xml|hdf5|h5))", text)
    if not match:
        return None
    return match.group(1)


def apply_text_overrides(config: Dict[str, Any], text: str) -> None:
    low = text.lower()
    energy = _parse_source_energy_mev(text)
    if energy is not None:
        config["source"]["energy"] = float(energy)
    pos = _parse_triplet(text, "position")
    if pos:
        config["source"]["position"] = pos
    direction = _parse_triplet(text, "direction")
    if direction:
        config["source"]["direction"] = direction
    at_to = re.search(
        r"\bat\s*\(?\s*([-+]?\d*\.?\d+)\s*[, ]\s*([-+]?\d*\.?\d+)\s*[, ]\s*([-+]?\d*\.?\d+)\s*\)?\s*"
        r"(?:to|towards|->)\s*"
        r"\(?\s*([-+]?\d*\.?\d+)\s*[, ]\s*([-+]?\d*\.?\d+)\s*[, ]\s*([-+]?\d*\.?\d+)\s*\)?",
        low,
    )
    if at_to:
        if not config["source"].get("position"):
            config["source"]["position"] = {
                "type": "vector",
                "value": [float(at_to.group(1)), float(at_to.group(2)), float(at_to.group(3))],
            }
        if not config["source"].get("direction"):
            config["source"]["direction"] = {
                "type": "vector",
                "value": [float(at_to.group(4)), float(at_to.group(5)), float(at_to.group(6))],
            }
    if not config["source"].get("position"):
        inferred_pos = _infer_position_from_text(text)
        if inferred_pos:
            config["source"]["position"] = inferred_pos
    if not config["source"].get("direction"):
        inferred_dir = _infer_direction_from_text(text)
        if inferred_dir:
            config["source"]["direction"] = inferred_dir

    if "point source" in low or "point-like" in low:
        config["source"]["type"] = "point"
    elif "beam" in low:
        config["source"]["type"] = "beam"
    elif "isotropic" in low:
        config["source"]["type"] = "isotropic"

    out_path = _parse_output_path(text)
    if out_path:
        config["output"]["path"] = out_path
    if not config["output"].get("path") and config["output"].get("format"):
        fmt = str(config["output"]["format"]).strip().lower()
        if fmt:
            config["output"]["path"] = f"output/result.{fmt}"


def ensure_material_volume_map(config: Dict[str, Any]) -> None:
    mats = config.get("materials", {}).get("selected_materials", []) or []
    vmap = config.get("materials", {}).get("volume_material_map", {})
    if not isinstance(vmap, dict):
        return
    if vmap or not mats:
        return
    if not config.get("geometry", {}).get("structure"):
        return
    config["materials"]["volume_material_map"] = {"target": mats[0]}


def export_min_config(config: Dict[str, Any]) -> Dict[str, Any]:
    vmap = config["materials"].get("volume_material_map", {}) or {}
    if isinstance(vmap, dict):
        volume_material_map = [{"volume": k, "material": v} for k, v in vmap.items() if k and v]
    elif isinstance(vmap, list):
        volume_material_map = vmap
    else:
        volume_material_map = []
    if not volume_material_map and config["materials"].get("selected_materials"):
        volume_material_map = [{"volume": "target", "material": config["materials"]["selected_materials"][0]}]

    return {
        "geometry": {
            "graph_program": config["geometry"].get("graph_program"),
            "structure": config["geometry"].get("structure"),
            "params": config["geometry"].get("params", {}),
        },
        "materials": {
            "volume_material_map": volume_material_map,
            "environment": {
                "temperature_K": config["environment"].get("temperature"),
                "pressure_Pa": config["environment"].get("pressure"),
            },
        },
        "physics_list": {
            "name": config["physics"].get("physics_list"),
        },
        "source": {
            "particle": config["source"].get("particle"),
            "energy_MeV": config["source"].get("energy"),
            "position": config["source"].get("position"),
            "direction": config["source"].get("direction"),
        },
        "output": {
            "format": config["output"].get("format"),
            "path": config["output"].get("path"),
        },
    }


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (dict, list)) and len(value) == 0:
        return True
    return False


def _collect_required_missing(schema: Dict[str, Any], obj: Any, prefix: str = "") -> List[str]:
    missing: List[str] = []
    if not isinstance(schema, dict):
        return missing
    if schema.get("type") != "object":
        return missing

    props = schema.get("properties", {})
    required = schema.get("required", [])
    value = obj if isinstance(obj, dict) else {}

    for key in required:
        path = f"{prefix}.{key}" if prefix else key
        if key not in value or _is_missing_value(value.get(key)):
            missing.append(path)

    for key, sub_schema in props.items():
        if key in value and value.get(key) is not None:
            path = f"{prefix}.{key}" if prefix else key
            missing.extend(_collect_required_missing(sub_schema, value.get(key), path))

    return missing


def compute_missing(config: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    if config["geometry"].get("structure") and config["geometry"].get("missing_params"):
        for path in config["geometry"]["missing_params"]:
            missing.append(f"geometry.params.{path}")
    try:
        schema = _load_json(SCHEMA_PATH)
        exported = export_min_config(config)
        missing.extend(_collect_required_missing(schema, exported))
    except Exception:
        pass
    dedup: List[str] = []
    seen = set()
    for item in missing:
        if item not in seen:
            dedup.append(item)
            seen.add(item)
    return dedup


def build_user_friendly(config: Dict[str, Any]) -> str:
    geo = config["geometry"]
    geo_label = geo.get("structure") or (geo.get("chosen_skeleton") or "unknown")
    return "\n".join(
        [
            f"Geometry: {geo_label}",
            f"Feasible: {geo.get('feasible')}",
            f"Materials: {', '.join(config['materials']['selected_materials']) or 'missing'}",
            f"Particle: {config['source']['particle'] or 'missing'}",
            f"Source type: {config['source']['type'] or 'missing'}",
            f"Physics list: {config['physics']['physics_list'] or 'missing'}",
            f"Output format: {config['output']['format'] or 'missing'}",
            f"Output path: {config['output'].get('path') or 'missing'}",
        ]
    )
