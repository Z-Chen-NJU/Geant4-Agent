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
