from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from nlu.llm_support.ollama_client import chat, extract_json
from ui.web.runtime_state import get_ollama_config_path


def heuristic_focus(text: str) -> List[str]:
    low = text.lower()
    focus = []
    geom_keys = ["box", "tubs", "ring", "grid", "stack", "nest", "shell", "cylinder", "sphere"]
    if any(key in low for key in geom_keys):
        focus.append("geometry")
    if any(key in low for key in ["material", "steel", "aluminum", "g4_"]):
        focus.append("materials")
    if any(key in low for key in ["source", "beam", "gamma", "electron", "proton", "neutron"]):
        focus.append("source")
    if any(key in low for key in ["physics list", "ftfp", "qgsp", "qb"]):
        focus.append("physics")
    return focus or ["geometry"]


def infer_geometry_hint(text: str) -> Optional[str]:
    low = text.lower()
    if any(key in low for key in ["cube", "box", "立方体", "长方体"]):
        return "single_box"
    if any(key in low for key in ["cylinder", "tubs", "圆柱"]):
        return "single_tubs"
    return None


def has_explicit_geometry_assignment(text: str) -> bool:
    low = text.lower()
    if re.search(r"\b(structure|geometry)\s*[:=]", low):
        return True
    if re.search(r"(几何|结构)\s*[:=]", text):
        return True

    shape_tokens = (
        "ring",
        "grid",
        "stack",
        "nest",
        "shell",
        "box",
        "cube",
        "cylinder",
        "tubs",
        "sphere",
        "cons",
        "trd",
        "polycone",
        "cuttubs",
        "boolean",
        "环形",
        "阵列",
        "堆叠",
        "嵌套",
        "壳层",
        "立方体",
        "圆柱",
        "球",
    )
    verb_tokens = (
        "use",
        "build",
        "create",
        "make",
        "set",
        "change",
        "switch",
        "update",
        "改成",
        "改为",
        "换成",
        "改用",
        "设置",
    )
    has_shape = any(token in low or token in text for token in shape_tokens)
    has_verb = any(token in low or token in text for token in verb_tokens)
    return has_shape and has_verb


def should_freeze_geometry_update(
    *,
    text: str,
    routed: Dict[str, object],
    existing_structure: Optional[str],
    incoming_structure: Optional[str],
    incoming_params: Dict[str, float],
    previous_missing_fields: List[str],
) -> Tuple[bool, str]:
    if not existing_structure:
        return False, ""
    explicit_geo = has_explicit_geometry_assignment(text)
    if explicit_geo:
        return False, ""

    focus = routed.get("focus", [])
    focus_set = {str(item).strip().lower() for item in focus if isinstance(item, str)}
    geom_missing_before = any(field.startswith("geometry.params.") for field in previous_missing_fields)

    if incoming_structure and incoming_structure != existing_structure:
        return True, "structure_change_without_explicit_request"
    if not geom_missing_before and "geometry" not in focus_set and (incoming_structure or incoming_params):
        return True, "non_geometry_turn_locked"
    return False, ""


def route_with_llm(text: str, missing_fields: List[str]) -> Dict[str, object]:
    prompt = (
        "You are a router that decides which modules to run next in a Geant4 config builder.\n"
        "Return JSON with keys: use_geometry_bert (bool), focus (list of strings: geometry, materials, source, physics), "
        "geometry_hint (optional: single_box or single_tubs), reason (string).\n"
        f"User text: {text}\n"
        f"Missing fields: {missing_fields}\n"
        "JSON:"
    )
    try:
        resp = chat(prompt, config_path=get_ollama_config_path(), temperature=0.0)
        parsed = extract_json(resp.get("response", "")) or {}
        if isinstance(parsed, dict) and "focus" in parsed:
            return parsed
    except Exception:
        return {}
    return {}


def decide_focus(text: str, missing_fields: List[str], llm_router: bool) -> Dict[str, object]:
    allowed_focus = {"geometry", "materials", "source", "physics"}

    def sanitize_routed(routed: Dict[str, object]) -> Dict[str, object]:
        focus_raw = routed.get("focus", [])
        if not isinstance(focus_raw, list):
            focus_raw = []
        focus: List[str] = []
        for item in focus_raw:
            if not isinstance(item, str):
                continue
            value = item.strip().lower()
            if value in allowed_focus and value not in focus:
                focus.append(value)
        if not focus:
            focus = heuristic_focus(text)

        hint = str(routed.get("geometry_hint", "")).strip().lower()
        if hint not in {
            "",
            "ring",
            "grid",
            "nest",
            "stack",
            "shell",
            "single_box",
            "single_tubs",
            "single_sphere",
            "single_cons",
            "single_trd",
            "single_polycone",
            "single_cuttubs",
            "boolean",
            "unknown",
        }:
            hint = ""

        use_geo = routed.get("use_geometry_bert")
        if not isinstance(use_geo, bool):
            use_geo = "geometry" in focus
        return {
            "use_geometry_bert": use_geo,
            "focus": focus,
            "geometry_hint": hint,
            "reason": str(routed.get("reason", "llm")).strip(),
        }

    if llm_router:
        routed = route_with_llm(text, missing_fields)
        if routed:
            return sanitize_routed(routed)
    focus = heuristic_focus(text)
    hint = infer_geometry_hint(text)
    return {
        "use_geometry_bert": "geometry" in focus,
        "focus": focus,
        "geometry_hint": hint,
        "reason": "heuristic",
    }
