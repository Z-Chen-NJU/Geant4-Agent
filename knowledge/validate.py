from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from core.config.output_format_registry import accepted_output_formats


@dataclass
class ValidationIssue:
    level: str
    message: str


def _load_materials(path: str | Path) -> List[str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data.get("materials", []))


def validate_material_spec(
    spec: Dict[str, object],
    materials_path: str | Path = "knowledge/data/materials_geant4_nist.json",
) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if "material" not in spec:
        issues.append(ValidationIssue("error", "Missing required field: material"))
        return issues

    materials = _load_materials(materials_path)
    mat = str(spec.get("material"))
    if mat not in materials:
        issues.append(ValidationIssue("error", f"Unknown material: {mat}"))

    if "temperature_K" in spec and float(spec["temperature_K"]) < 0:
        issues.append(ValidationIssue("error", "temperature_K must be >= 0"))
    if "pressure_Pa" in spec and float(spec["pressure_Pa"]) < 0:
        issues.append(ValidationIssue("error", "pressure_Pa must be >= 0"))
    if "density_g_cm3" in spec and float(spec["density_g_cm3"]) < 0:
        issues.append(ValidationIssue("error", "density_g_cm3 must be >= 0"))
    return issues


def validate_environment_spec(spec: Dict[str, object]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if "temperature_K" in spec and float(spec["temperature_K"]) < 0:
        issues.append(ValidationIssue("error", "temperature_K must be >= 0"))
    if "pressure_Pa" in spec and float(spec["pressure_Pa"]) < 0:
        issues.append(ValidationIssue("error", "pressure_Pa must be >= 0"))
    # Optional sanity bounds from local constraints file
    constraints_path = Path("knowledge/data/environment_constraints.json")
    if constraints_path.exists():
        c = json.loads(constraints_path.read_text(encoding="utf-8"))
        if "temperature_K" in spec:
            max_t = float(c.get("temperature_K", {}).get("max", float("inf")))
            if float(spec["temperature_K"]) > max_t:
                issues.append(ValidationIssue("warning", "temperature_K exceeds project bounds"))
        if "pressure_Pa" in spec:
            max_p = float(c.get("pressure_Pa", {}).get("max", float("inf")))
            if float(spec["pressure_Pa"]) > max_p:
                issues.append(ValidationIssue("warning", "pressure_Pa exceeds project bounds"))
    if "gas_mix" in spec:
        total = 0.0
        for comp in spec.get("gas_mix", []):
            if not isinstance(comp, dict):
                issues.append(ValidationIssue("error", "gas_mix items must be objects"))
                continue
            frac = float(comp.get("fraction", 0.0))
            if frac < 0.0 or frac > 1.0:
                issues.append(ValidationIssue("error", "gas_mix fraction must be in [0,1]"))
            total += frac
        if total > 1.001:
            issues.append(ValidationIssue("warning", "gas_mix fractions sum > 1.0"))
    return issues


def _load_list(path: str | Path) -> List[str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data.get("items", []))


def validate_min_config(config: Dict[str, object]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    # Validate physics list
    physics = config.get("physics", {})
    if not isinstance(physics, dict):
        physics = config.get("physics_list", {})
    if isinstance(physics, dict) and ("physics_list" in physics or "name" in physics):
        valid_lists = _load_list("knowledge/data/physics_lists.json")
        name = physics.get("physics_list", physics.get("name"))
        if name not in valid_lists:
            issues.append(ValidationIssue("warning", "physics.physics_list not in curated list"))
    # Validate source particle
    source = config.get("source", {})
    if isinstance(source, dict) and "particle" in source:
        valid_particles = _load_list("knowledge/data/particles.json")
        if source["particle"] not in valid_particles:
            issues.append(ValidationIssue("warning", "source.particle not in curated list"))
    # Validate output format
    output = config.get("output", {})
    if isinstance(output, dict) and "format" in output:
        valid_formats = accepted_output_formats()
        if output["format"] not in valid_formats:
            issues.append(ValidationIssue("warning", "output.format not in curated list"))

    # Validate source ranges
    source = config.get("source", {})
    if isinstance(source, dict):
        energy = source.get("energy", source.get("energy_MeV"))
        if energy is not None and float(energy) <= 0:
            issues.append(ValidationIssue("error", "source.energy must be > 0"))
        # Basic direction sanity
        direction = source.get("direction")
        vec = None
        if isinstance(direction, dict):
            vec = direction.get("value")
        elif isinstance(direction, list):
            vec = direction
        if isinstance(vec, list) and len(vec) == 3:
            if all(float(v) == 0.0 for v in vec):
                issues.append(ValidationIssue("error", "source.direction vector cannot be zero"))
        # Optional bounds
        constraints_path = Path("knowledge/data/source_constraints.json")
        if constraints_path.exists() and energy is not None:
            c = json.loads(constraints_path.read_text(encoding="utf-8"))
            max_e = float(c.get("energy_MeV", {}).get("max", float("inf")))
            if float(energy) > max_e:
                issues.append(ValidationIssue("warning", "source.energy exceeds project bounds"))

    # Validate volume-material map against provided volume names
    geometry = config.get("geometry", {})
    if isinstance(geometry, dict) and "volume_names" in geometry:
        vols = set(geometry.get("volume_names", []))
        raw_map = config.get("materials", {}).get("volume_material_map", [])
        mapped = set()
        if isinstance(raw_map, dict):
            for vol in raw_map.keys():
                if vol not in vols:
                    issues.append(ValidationIssue("warning", f"volume_material_map volume not in geometry.volume_names: {vol}"))
                mapped.add(vol)
        else:
            for item in raw_map:
                if isinstance(item, dict):
                    vol = item.get("volume")
                    if vol not in vols:
                        issues.append(ValidationIssue("warning", f"volume_material_map volume not in geometry.volume_names: {vol}"))
                    mapped.add(vol)
        missing = vols - mapped
        if missing:
            issues.append(ValidationIssue("warning", f"volume_material_map missing volumes: {sorted(missing)}"))
    return issues
