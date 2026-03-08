from __future__ import annotations

from typing import Iterable


def _joined(items: Iterable[str], *, lang: str, limit: int = 3) -> str:
    values = [str(item).strip() for item in items if str(item).strip()]
    if not values:
        return ""
    sep = "、" if lang == "zh" else ", "
    return sep.join(values[:limit])


def render_finalize_template(*, lang: str, confirmed_items: list[str] | None = None) -> str:
    confirmed = _joined(confirmed_items or [], lang=lang, limit=4)
    if lang == "zh":
        if confirmed:
            return f"配置已完成。当前已确认：{confirmed}。"
        return "配置已完成，可以继续导出或再做微调。"
    if confirmed:
        return f"Configuration complete. Confirmed items: {confirmed}."
    return "Configuration complete. You can export it now or keep refining it."


def render_update_status_template(*, lang: str, updated: list[str], remaining: list[str]) -> str:
    updated_text = _joined(updated, lang=lang)
    remaining_text = _joined(remaining, lang=lang, limit=2)
    if lang == "zh":
        if updated_text and remaining_text:
            return f"好的，已更新{updated_text}。接下来还需要{remaining_text}。"
        if updated_text:
            return f"好的，已更新{updated_text}。"
        if remaining_text:
            return f"当前还需要{remaining_text}。"
        return "当前配置已同步。"
    if updated_text and remaining_text:
        return f"Got it. I updated {updated_text}. I still need {remaining_text}."
    if updated_text:
        return f"Got it. I updated {updated_text}."
    if remaining_text:
        return f"I still need {remaining_text}."
    return "Configuration state synchronized."


def render_overwrite_confirmation_template(*, lang: str, preview_lines: list[str]) -> str:
    detail = "；".join(preview_lines[:2]) if lang == "zh" else "; ".join(preview_lines[:2])
    if lang == "zh":
        return (
            "我检测到这会覆盖已经确认的值。"
            f"待修改内容：{detail}。"
            "如果要应用这些修改，请直接回复“确认”；"
            "如果要保留原值，请直接说“保持原值”。"
        )
    return (
        "This would overwrite an already confirmed value. "
        f"Pending change: {detail}. "
        "Reply 'confirm' to apply it, or say 'keep existing' to keep the current value."
    )


def render_overwrite_rejection_template(*, lang: str, fields: list[str], remaining: list[str]) -> str:
    fields_text = _joined(fields, lang=lang)
    remaining_text = _joined(remaining, lang=lang, limit=2)
    if lang == "zh":
        if fields_text and remaining_text:
            return f"好的，已保留{fields_text}的原有值。接下来还需要{remaining_text}。"
        if fields_text:
            return f"好的，已保留{fields_text}的原有值。"
        if remaining_text:
            return f"好的，这次覆盖不会应用。接下来还需要{remaining_text}。"
        return "好的，这次覆盖不会应用，当前会保留原有配置。"
    if fields_text and remaining_text:
        return f"Okay. I kept the current value for {fields_text}. I still need {remaining_text}."
    if fields_text:
        return f"Okay. I kept the current value for {fields_text}."
    if remaining_text:
        return f"Okay. I did not apply that overwrite. I still need {remaining_text}."
    return "Okay. I did not apply that overwrite and kept the current configuration."


def render_grouped_progress_template(*, lang: str, grouped: dict) -> str:
    if not isinstance(grouped, dict) or not grouped:
        return ""
    lines: list[str] = []
    for domain in ("geometry", "materials", "source", "physics", "output"):
        item = grouped.get(domain)
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or domain)
        updated = [str(x) for x in item.get("updated_fields", []) if str(x)]
        pending = [str(x) for x in item.get("pending_fields", []) if str(x)]
        confirmed = [str(x) for x in item.get("confirmed_fields", []) if str(x)]
        if not (updated or pending or confirmed):
            continue
        if lang == "zh":
            segments: list[str] = []
            if updated:
                segments.append(f"已同步{_joined(updated, lang=lang)}")
            elif confirmed:
                segments.append(f"已确认{_joined(confirmed, lang=lang, limit=2)}")
            if pending:
                segments.append(f"待补充{_joined(pending, lang=lang, limit=2)}")
            if segments:
                lines.append(f"{label}：{'；'.join(segments)}。")
        else:
            segments = []
            if updated:
                segments.append(f"updated {_joined(updated, lang=lang)}")
            elif confirmed:
                segments.append(f"confirmed {_joined(confirmed, lang=lang, limit=2)}")
            if pending:
                segments.append(f"still needs {_joined(pending, lang=lang, limit=2)}")
            if segments:
                lines.append(f"{label}: {'; '.join(segments)}.")
    return "".join(lines) if lang == "zh" else " ".join(lines)
