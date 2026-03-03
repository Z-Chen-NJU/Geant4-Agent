from __future__ import annotations

from core.config.field_registry import friendly_labels
from core.config.prompt_registry import clarification_fallback, completion_message
from core.dialogue.types import DialogueAction, DialogueDecision
from planner.question_renderer import render_question


def _render_update_status(decision: DialogueDecision, *, lang: str) -> str:
    updated = friendly_labels(decision.updated_paths[:3], lang)
    remaining = friendly_labels(decision.missing_fields[:2], lang)
    if lang == "zh":
        if updated and remaining:
            return f"\u5df2\u66f4\u65b0\uff1a{', '.join(updated)}\u3002\u4ecd\u9700\u8865\u5145\uff1a{', '.join(remaining)}\u3002"
        if updated:
            return f"\u5df2\u66f4\u65b0\uff1a{', '.join(updated)}\u3002"
        if remaining:
            return f"\u5f53\u524d\u4ecd\u9700\u8865\u5145\uff1a{', '.join(remaining)}\u3002"
        return "\u5f53\u524d\u914d\u7f6e\u5df2\u540c\u6b65\u3002"
    if updated and remaining:
        return f"Updated: {', '.join(updated)}. Still needed: {', '.join(remaining)}."
    if updated:
        return f"Updated: {', '.join(updated)}."
    if remaining:
        return f"Still needed: {', '.join(remaining)}."
    return "Configuration state synchronized."


def _render_overwrite_confirmation(decision: DialogueDecision, *, lang: str) -> str:
    preview = decision.overwrite_preview[:2]
    parts: list[str] = []
    for item in preview:
        field = item.get("field", item.get("path", ""))
        old_value = item.get("old")
        new_value = item.get("new")
        parts.append(f"{field}: {old_value} -> {new_value}")
    if lang == "zh":
        detail = "\uff1b".join(parts)
        return (
            f"\u68c0\u6d4b\u5230\u5c06\u8986\u76d6\u5df2\u786e\u8ba4\u7684\u5185\u5bb9\u3002"
            f"\u8bf7\u786e\u8ba4\u662f\u5426\u5e94\u7528\u4ee5\u4e0b\u4fee\u6539\uff1a{detail}\u3002"
        )
    detail = "; ".join(parts)
    return f"An existing confirmed value would be overwritten. Please confirm whether to apply this change: {detail}."


def render_dialogue_message(
    decision: DialogueDecision,
    *,
    lang: str,
    use_llm_question: bool,
    ollama_config: str,
    user_temperature: float,
    dialogue_summary: dict | None = None,
) -> str:
    if decision.action == DialogueAction.FINALIZE:
        return completion_message(lang)
    if decision.action == DialogueAction.CONFIRM_OVERWRITE:
        return _render_overwrite_confirmation(decision, lang=lang)
    if decision.action == DialogueAction.ASK_CLARIFICATION:
        if use_llm_question:
            return render_question(
                decision.asked_fields,
                lang=lang,
                ollama_config=ollama_config,
                temperature=user_temperature,
            )
        return clarification_fallback(friendly_labels(decision.asked_fields, lang), lang)
    if decision.action == DialogueAction.SUMMARIZE_PROGRESS:
        summary = dialogue_summary or {}
        updated = summary.get("updated_fields") or friendly_labels(decision.updated_paths[:3], lang)
        pending = summary.get("pending_fields") or friendly_labels(decision.missing_fields[:2], lang)
        recent = summary.get("recent_confirmed") or []
        if lang == "zh":
            parts: list[str] = []
            if updated:
                parts.append(f"\u672c\u8f6e\u5df2\u540c\u6b65\uff1a{', '.join(updated)}\u3002")
            if recent:
                parts.append(f"\u5f53\u524d\u5df2\u786e\u8ba4\uff1a{', '.join(recent[:3])}\u3002")
            if pending:
                parts.append(f"\u4ecd\u9700\u8865\u5145\uff1a{', '.join(pending[:2])}\u3002")
            return "".join(parts) or "\u5f53\u524d\u914d\u7f6e\u6b63\u5728\u6536\u655b\u3002"
        parts = []
        if updated:
            parts.append(f"Updated this turn: {', '.join(updated)}.")
        if recent:
            parts.append(f"Confirmed so far: {', '.join(recent[:3])}.")
        if pending:
            parts.append(f"Still needed: {', '.join(pending[:2])}.")
        return " ".join(parts) or "Configuration is converging."
    if decision.action in {DialogueAction.CONFIRM_UPDATE, DialogueAction.ANSWER_STATUS}:
        return _render_update_status(decision, lang=lang)
    return completion_message(lang)
