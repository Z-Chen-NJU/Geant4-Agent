from __future__ import annotations

import re
from typing import Any

from core.orchestrator.types import Intent
from nlu.bert_lab.llm_bridge import build_normalization_prompt
from nlu.bert_lab.ollama_client import chat, extract_json


_TARGET_HINTS = {
    "geometry.params.module_x": ["module_x", "x=", "x:", "宽", "x方向"],
    "geometry.params.module_y": ["module_y", "y=", "y:", "高", "y方向"],
    "geometry.params.module_z": ["module_z", "z=", "z:", "厚", "z方向"],
    "geometry.structure": ["structure", "geometry", "box", "cube", "sphere", "cylinder", "ring", "grid"],
    "materials.selected_materials": ["material", "铜", "copper", "g4_"],
    "source.type": ["source type", "point", "beam", "isotropic", "点源", "束流"],
    "source.particle": ["gamma", "electron", "proton", "particle", "粒子"],
    "source.energy": ["mev", "gev", "kev", "能量"],
    "source.position": ["position", "origin", "center", "位置", "原点", "中心"],
    "source.direction": ["direction", "+z", "-z", "+x", "-x", "+y", "-y", "方向"],
    "physics.physics_list": ["physics list", "物理列表", "ftfp", "qgsp", "qbbc", "shielding"],
    "output.format": ["output format", "root", "json", "csv", "输出格式"],
    "output.path": ["output path", ".root", ".json", ".csv", "输出路径"],
}


def _infer_intent(text: str) -> Intent:
    low = text.lower()
    if any(k in low for k in ["改", "修改", "change", "switch", "update", "set", "设为"]):
        return Intent.MODIFY
    if any(k in low for k in ["删除", "remove", "清空"]):
        return Intent.REMOVE
    if any(k in low for k in ["确认", "对吗", "is it", "confirm"]):
        return Intent.CONFIRM
    if "?" in text or "？" in text:
        return Intent.QUESTION
    return Intent.SET


def _infer_target_paths(text: str, normalized_text: str) -> list[str]:
    payload = (text + " ; " + normalized_text).lower()
    out: list[str] = []
    for path, hints in _TARGET_HINTS.items():
        if any(h.lower() in payload for h in hints):
            out.append(path)
    if not out:
        out.append("geometry.structure")
    return sorted(set(out))


def normalize_user_turn(
    user_text: str,
    context_summary: str,
    config_path: str,
) -> dict[str, Any]:
    prompt = build_normalization_prompt(user_text, context_summary=context_summary)
    normalized_text = ""
    structure_hint = ""
    confidence = 0.6
    try:
        resp = chat(prompt, config_path=config_path, temperature=0.0)
        parsed = extract_json(resp.get("response", ""))
        if isinstance(parsed, dict):
            normalized_text = str(parsed.get("normalized_text", "")).strip()
            structure_hint = str(parsed.get("structure_hint", "")).strip()
            confidence = 0.8 if normalized_text else 0.6
    except Exception:
        normalized_text = ""

    if not normalized_text:
        normalized_text = user_text
        confidence = 0.4

    intent = _infer_intent(user_text)
    target_paths = _infer_target_paths(user_text, normalized_text)
    # Protect against ambiguous turns that should not rewrite locked fields.
    if re.search(r"\b(为什么|why|reason|理由)\b", user_text.lower()):
        intent = Intent.QUESTION
    return {
        "intent": intent,
        "target_paths": target_paths,
        "normalized_text": normalized_text,
        "structure_hint": structure_hint,
        "confidence": confidence,
    }
