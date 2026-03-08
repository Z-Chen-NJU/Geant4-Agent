from __future__ import annotations

from core.config.field_registry import friendly_label, friendly_labels, missing_field_question
from core.config.prompt_registry import clarification_fallback, completion_message
from core.dialogue.action_templates import (
    render_finalize_template,
    render_grouped_progress_template,
    render_overwrite_confirmation_template,
    render_overwrite_rejection_template,
    render_update_status_template,
)
from core.dialogue.types import DialogueAction, DialogueDecision
from planner.question_renderer import render_naturalized_response, render_question


def _render_update_status(decision: DialogueDecision, *, lang: str) -> str:
    return render_update_status_template(
        lang=lang,
        updated=friendly_labels(decision.updated_paths[:3], lang),
        remaining=friendly_labels(decision.missing_fields[:2], lang),
    )


def _format_preview_item(item: dict, *, lang: str) -> str:
    path = str(item.get("path", "")).strip()
    field = str(item.get("field") or (friendly_label(path, lang) if path else "")).strip()
    old_value = item.get("old")
    new_value = item.get("new")
    if lang == "zh":
        return f"{field}：{old_value} -> {new_value}"
    return f"{field}: {old_value} -> {new_value}"


def _render_overwrite_confirmation(decision: DialogueDecision, *, lang: str) -> str:
    preview = decision.overwrite_preview[:2]
    parts = [_format_preview_item(item, lang=lang) for item in preview]
    return render_overwrite_confirmation_template(lang=lang, preview_lines=parts)


def _render_overwrite_rejection(decision: DialogueDecision, *, lang: str) -> str:
    preview = decision.overwrite_preview[:2]
    fields = [friendly_label(str(item.get("path", "")), lang) for item in preview if str(item.get("path", "")).strip()]
    return render_overwrite_rejection_template(
        lang=lang,
        fields=fields,
        remaining=friendly_labels(decision.missing_fields[:2], lang),
    )


def _render_choice_explanation(decision: DialogueDecision, *, lang: str, dialogue_summary: dict | None) -> str:
    explanation = dict(decision.explanation or {})
    if not explanation and dialogue_summary:
        explanation = dict(dialogue_summary.get("available_explanations", {}) or {})
    if not explanation:
        return _render_update_status(decision, lang=lang)

    lines: list[str] = []
    for domain in ("physics", "materials", "source"):
        item = explanation.get(domain)
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or domain)
        field_raw = str(item.get("field") or label)
        field = friendly_label(field_raw, lang) if "." in field_raw else field_raw
        source = str(item.get("source") or "unknown")
        reasons = [str(reason) for reason in item.get("reasons", []) if str(reason)]
        if lang == "zh":
            segments = [f"{label}：{field}。", f"来源：{source}。"]
            if reasons:
                segments.append(f"原因：{'；'.join(reasons[:2])}。")
            lines.append("".join(segments))
        else:
            segments = [f"{label}: {field}.", f"Source: {source}."]
            if reasons:
                segments.append(f"Reason: {'; '.join(reasons[:2])}.")
            lines.append(" ".join(segments))
    if lines:
        return " ".join(lines) if lang != "zh" else "".join(lines)
    return _render_update_status(decision, lang=lang)


def _render_grouped_progress(summary: dict, *, lang: str) -> str:
    grouped = summary.get("grouped_status", {}) if isinstance(summary, dict) else {}
    return render_grouped_progress_template(lang=lang, grouped=grouped)


def _render_structured_clarification(paths: list[str], *, lang: str) -> str:
    if not paths:
        return clarification_fallback([], lang)
    if len(paths) == 1:
        return missing_field_question(paths[0], lang)
    questions = [missing_field_question(path, lang) for path in paths[:2]]
    if lang == "zh":
        return "还需要补充两项信息。 " + " ".join(questions)
    return "I still need two details. " + " ".join(questions)


def render_dialogue_message(
    decision: DialogueDecision,
    *,
    lang: str,
    use_llm_question: bool,
    ollama_config: str,
    user_temperature: float,
    dialogue_summary: dict | None = None,
    raw_dialogue: list[dict] | None = None,
) -> str:
    recent_user_text = ""
    for item in reversed(list(raw_dialogue or [])):
        if item.get("role") == "user":
            recent_user_text = str(item.get("content", "")).strip()
            break
    confirmed_items = list((dialogue_summary or {}).get("recent_confirmed", []) or [])

    def _maybe_naturalize(text: str) -> str:
        if not use_llm_question or not text:
            return text
        if decision.action == DialogueAction.ASK_CLARIFICATION:
            return text
        return render_naturalized_response(
            text,
            lang=lang,
            action=decision.action.value,
            updated_paths=decision.updated_paths,
            missing_fields=decision.missing_fields,
            asked_fields=decision.asked_fields,
            overwrite_preview=decision.overwrite_preview,
            dialogue_summary=dialogue_summary,
            raw_dialogue=raw_dialogue,
            ollama_config=ollama_config,
            temperature=user_temperature,
        )

    if decision.action == DialogueAction.FINALIZE:
        confirmed = list((dialogue_summary or {}).get("recent_confirmed", []) or [])
        return _maybe_naturalize(render_finalize_template(lang=lang, confirmed_items=confirmed) or completion_message(lang))
    if decision.action == DialogueAction.CONFIRM_OVERWRITE:
        return _maybe_naturalize(_render_overwrite_confirmation(decision, lang=lang))
    if decision.action == DialogueAction.REJECT_OVERWRITE:
        return _maybe_naturalize(_render_overwrite_rejection(decision, lang=lang))
    if decision.action == DialogueAction.EXPLAIN_CHOICE:
        return _maybe_naturalize(_render_choice_explanation(decision, lang=lang, dialogue_summary=dialogue_summary))
    if decision.action == DialogueAction.ASK_CLARIFICATION:
        if use_llm_question:
            return render_question(
                decision.asked_fields,
                lang=lang,
                ollama_config=ollama_config,
                temperature=user_temperature,
                recent_user_text=recent_user_text,
                confirmed_items=confirmed_items,
            )
        return _render_structured_clarification(decision.asked_fields, lang=lang)
    if decision.action == DialogueAction.SUMMARIZE_PROGRESS:
        summary = dialogue_summary or {}
        grouped = _render_grouped_progress(summary, lang=lang)
        if grouped:
            return _maybe_naturalize(grouped)
        updated = summary.get("updated_fields") or friendly_labels(decision.updated_paths[:3], lang)
        pending = summary.get("pending_fields") or friendly_labels(decision.missing_fields[:2], lang)
        recent = summary.get("recent_confirmed") or []
        if lang == "zh":
            parts: list[str] = []
            if updated:
                parts.append(f"本轮已同步：{', '.join(updated)}。")
            if recent:
                parts.append(f"当前已确认：{', '.join(recent[:3])}。")
            if pending:
                parts.append(f"仍需补充：{', '.join(pending[:2])}。")
            return _maybe_naturalize("".join(parts) or "当前配置正在收敛。")
        parts = []
        if updated:
            parts.append(f"Updated this turn: {', '.join(updated)}.")
        if recent:
            parts.append(f"Confirmed so far: {', '.join(recent[:3])}.")
        if pending:
            parts.append(f"Still needed: {', '.join(pending[:2])}.")
        return _maybe_naturalize(" ".join(parts) or "Configuration is converging.")
    if decision.action in {DialogueAction.CONFIRM_UPDATE, DialogueAction.ANSWER_STATUS}:
        return _maybe_naturalize(_render_update_status(decision, lang=lang))
    return _maybe_naturalize(completion_message(lang))
