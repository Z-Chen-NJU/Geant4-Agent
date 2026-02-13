from __future__ import annotations

from typing import Dict, Iterable, List
import json


PARAM_DESCRIPTIONS: Dict[str, str] = {
    "module_x": "module size in x (mm)",
    "module_y": "module size in y (mm)",
    "module_z": "module size in z (mm)",
    "nx": "number of modules along x (integer)",
    "ny": "number of modules along y (integer)",
    "pitch_x": "grid pitch in x (mm)",
    "pitch_y": "grid pitch in y (mm)",
    "n": "number of modules on ring (integer)",
    "radius": "ring radius (mm)",
    "clearance": "clearance/gap (mm)",
    "parent_x": "parent box size x (mm)",
    "parent_y": "parent box size y (mm)",
    "parent_z": "parent box size z (mm)",
    "child_rmax": "child cylinder outer radius (mm)",
    "child_hz": "child cylinder half-length (mm)",
    "rmax1": "cone max radius at -z side (mm)",
    "rmax2": "cone max radius at +z side (mm)",
    "x1": "trd half-length in x at -z side (mm)",
    "x2": "trd half-length in x at +z side (mm)",
    "y1": "trd half-length in y at -z side (mm)",
    "y2": "trd half-length in y at +z side (mm)",
    "z1": "polycone z plane 1 (mm)",
    "z2": "polycone z plane 2 (mm)",
    "z3": "polycone z plane 3 (mm)",
    "r1": "polycone radius at z1 (mm)",
    "r2": "polycone radius at z2 (mm)",
    "r3": "polycone radius at z3 (mm)",
    "tilt_x": "cuttubs cut tilt in x (deg proxy)",
    "tilt_y": "cuttubs cut tilt in y (deg proxy)",
    "bool_a_x": "boolean left box x (mm)",
    "bool_a_y": "boolean left box y (mm)",
    "bool_a_z": "boolean left box z (mm)",
    "bool_b_x": "boolean right box x (mm)",
    "bool_b_y": "boolean right box y (mm)",
    "bool_b_z": "boolean right box z (mm)",
    "inner_r": "inner radius (mm)",
    "th1": "shell thickness 1 (mm)",
    "th2": "shell thickness 2 (mm)",
    "th3": "shell thickness 3 (mm)",
    "hz": "shell half-length (mm)",
    "stack_x": "stack footprint x (mm)",
    "stack_y": "stack footprint y (mm)",
    "t1": "layer thickness 1 (mm)",
    "t2": "layer thickness 2 (mm)",
    "t3": "layer thickness 3 (mm)",
    "stack_clearance": "clearance between stacked layers (mm)",
    "nest_clearance": "clearance for nesting (mm)",
    "tx": "translation x (mm)",
    "ty": "translation y (mm)",
    "tz": "translation z (mm)",
    "rx": "rotation around x (deg)",
    "ry": "rotation around y (deg)",
    "rz": "rotation around z (deg)",
}


def describe_params(keys: Iterable[str]) -> List[str]:
    lines: List[str] = []
    for k in keys:
        desc = PARAM_DESCRIPTIONS.get(k, k)
        lines.append(f"- {k}: {desc}")
    return lines


def build_missing_params_schema(structure: str, missing: Iterable[str]) -> Dict[str, object]:
    keys = list(missing)
    properties: Dict[str, object] = {}
    required: List[str] = []
    for k in keys:
        typ = "integer" if k in {"nx", "ny", "n"} else "number"
        properties[k] = {"type": typ, "description": PARAM_DESCRIPTIONS.get(k, k)}
        required.append(k)
    return {
        "title": f"{structure} missing parameters",
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def build_missing_params_prompt(structure: str, missing: Iterable[str], fmt: str = "text") -> str:
    missing_list = list(missing)
    if not missing_list:
        return ""
    if fmt == "json_schema":
        schema = build_missing_params_schema(structure, missing_list)
        return (
            "Return a JSON object that satisfies this JSON schema:\n"
            + json.dumps(schema, ensure_ascii=False, indent=2)
        )
    header = (
        "Some required geometry parameters are missing. "
        "Please provide the following values (numbers, units in mm if not specified):"
    )
    lines = "\n".join(describe_params(missing_list))
    return f"[structure={structure}]\n{header}\n{lines}\nReturn a JSON object with these keys."


def build_normalization_prompt(user_text: str) -> str:
    return (
        "Rewrite the user request into controlled English for downstream BERT parsing.\n"
        "Output JSON only with keys:\n"
        "- normalized_text: string\n"
        "- language_detected: string\n"
        "- structure_hint: one of [ring, grid, nest, stack, shell, single_box, single_tubs, single_sphere, single_cons, single_trd, single_polycone, single_cuttubs, boolean, unknown]\n"
        "Normalization rules:\n"
        "- Preserve all numeric values and units exactly (do not convert or round).\n"
        "- Prefer this compact style in normalized_text:\n"
        "  geometry_intent: <circular_placement|planar_array|containment_parent_child|z_layer_sequence|coaxial_shells|single_box|single_tubs|single_sphere|single_cons|single_trd|single_polycone|single_cuttubs|boolean|unresolved>; ...\n"
        "- If geometry is ambiguous, use:\n"
        "  geometry_intent: unresolved; candidate_pattern: <intent_a> | <intent_b>; ...\n"
        "- Keep text concise and field-like (semicolon-separated clauses), no narrative sentences.\n"
        "- Include only information present in user text; do not hallucinate values.\n"
        "- No explanation or markdown.\n"
        f"User text: {user_text}\n"
        "JSON:"
    )


