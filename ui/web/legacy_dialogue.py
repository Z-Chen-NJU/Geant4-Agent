from __future__ import annotations

from typing import Any, Dict, List, Tuple

from core.config.field_registry import friendly_labels
from core.config.phase_registry import select_phase_fields
from core.config.prompt_registry import clarification_fallback
from planner.agent import ask_missing
from ui.web.runtime_state import get_ollama_config_path


def is_complete(config: Dict[str, Any], missing_fields: List[str]) -> bool:
    if missing_fields:
        return False
    feasible = config.get("geometry", {}).get("feasible")
    if feasible is False:
        return False
    return True


def flatten(obj: Any, prefix: str = "") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            out.update(flatten(value, path))
        return out
    out[prefix] = obj
    return out


def diff_paths(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    before_flat = flatten(before)
    after_flat = flatten(after)
    keys = sorted(set(before_flat.keys()) | set(after_flat.keys()))
    changed: List[str] = []
    for key in keys:
        if before_flat.get(key) != after_flat.get(key):
            changed.append(key)
    return changed


def select_phase_and_fields(missing_fields: List[str]) -> Tuple[str, List[str]]:
    return select_phase_fields(missing_fields)


def friendly_fields(fields: List[str], lang: str) -> List[str]:
    return friendly_labels(fields, lang)


def ask_for_missing(
    asked_fields: List[str],
    asked_fields_friendly: List[str],
    history: List[Dict[str, str]],
    lang: str,
    *,
    use_llm: bool,
) -> str:
    if not asked_fields:
        return ""
    if not use_llm:
        return clarification_fallback(asked_fields_friendly, lang)
    return ask_missing(asked_fields, lang, get_ollama_config_path(), temperature=1.0)
