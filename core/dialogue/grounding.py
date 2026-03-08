from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge" / "data"


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _get_path(cfg: dict[str, Any], path: str) -> Any:
    cur: Any = cfg
    for seg in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(seg)
    return cur


@lru_cache(maxsize=1)
def _load_vocab() -> dict[str, list[str]]:
    physics = json.loads((KNOWLEDGE_DIR / "physics_lists.json").read_text(encoding="utf-8")).get("items", [])
    outputs = json.loads((KNOWLEDGE_DIR / "output_formats.json").read_text(encoding="utf-8")).get("items", [])
    return {
        "physics": [str(x) for x in physics if str(x)],
        "outputs": [str(x) for x in outputs if str(x)],
    }


def _find_mentions(text: str, items: list[str]) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for item in items:
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", flags=re.IGNORECASE)
        if pat.search(text):
            found.append(item)
    return found


def _conflicts(message: str, *, config: dict[str, Any]) -> bool:
    vocab = _load_vocab()

    physics_actual = _safe_str(_get_path(config, "physics.physics_list"))
    if physics_actual:
        mentions = _find_mentions(message, vocab["physics"])
        if mentions and all(m.lower() != physics_actual.lower() for m in mentions):
            return True

    output_actual = _safe_str(_get_path(config, "output.format"))
    if output_actual:
        mentions = _find_mentions(message, vocab["outputs"])
        if mentions and all(m.lower() != output_actual.lower() for m in mentions):
            return True

    return False


def _grounded_summary(config: dict[str, Any], *, lang: str) -> str:
    physics = _safe_str(_get_path(config, "physics.physics_list")) or ("未指定" if lang == "zh" else "not set")
    output_fmt = _safe_str(_get_path(config, "output.format")) or ("未指定" if lang == "zh" else "not set")
    source_type = _safe_str(_get_path(config, "source.type")) or ("未指定" if lang == "zh" else "not set")
    particle = _safe_str(_get_path(config, "source.particle")) or ("未指定" if lang == "zh" else "not set")
    if lang == "zh":
        return (
            f"当前已提交的配置是：物理列表 {physics}，输出格式 {output_fmt}，"
            f"源类型 {source_type}，粒子 {particle}。"
            "如果需要修改，请直接说明要改哪一项。"
        )
    return (
        f"Current committed config is: physics list {physics}, output format {output_fmt}, "
        f"source type {source_type}, particle {particle}. "
        "If you want changes, please specify which field to update."
    )


def enforce_message_grounding(message: str, *, config: dict[str, Any], action: str, lang: str) -> str:
    if not message:
        return message
    if action not in {"finalize", "summarize_progress", "answer_status", "confirm_update", "explain_choice"}:
        return message
    if _conflicts(message, config=config):
        return _grounded_summary(config, lang=lang)
    return message
