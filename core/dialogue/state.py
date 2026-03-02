from __future__ import annotations

from typing import Any

from core.config.field_registry import friendly_labels
from core.dialogue.types import DialogueDecision


def build_raw_dialogue(history: list[dict[str, Any]], *, limit: int = 12) -> list[dict[str, str]]:
    trimmed = history[-limit:]
    output: list[dict[str, str]] = []
    for item in trimmed:
        role = str(item.get("role", ""))
        content = str(item.get("content", ""))
        output.append({"role": role, "content": content})
    return output


def build_dialogue_summary(
    decision: DialogueDecision,
    *,
    lang: str,
    is_complete: bool,
    confirmed_fact_paths: list[str] | None = None,
    memory_depth: int = 0,
) -> dict[str, Any]:
    confirmed_fact_paths = confirmed_fact_paths or []
    return {
        "status": "complete" if is_complete else "pending",
        "last_action": decision.action.value,
        "user_intent": decision.user_intent,
        "updated_fields": friendly_labels(decision.updated_paths[:5], lang),
        "answered_fields": friendly_labels(decision.answered_this_turn[:5], lang),
        "pending_fields": friendly_labels(decision.missing_fields[:5], lang),
        "next_questions": friendly_labels(decision.asked_fields[:3], lang),
        "recent_confirmed": friendly_labels(confirmed_fact_paths[:5], lang),
        "memory_depth": memory_depth,
    }


def _merge_recent_paths(previous: list[str], incoming: list[str], *, limit: int) -> list[str]:
    merged = list(previous)
    for path in incoming:
        if not path:
            continue
        if path in merged:
            merged.remove(path)
        merged.insert(0, path)
    return merged[:limit]


def _build_memory_entry(decision: DialogueDecision, *, is_complete: bool) -> dict[str, Any]:
    return {
        "action": decision.action.value,
        "user_intent": decision.user_intent,
        "updated_paths": list(decision.updated_paths),
        "answered_this_turn": list(decision.answered_this_turn),
        "missing_fields": [] if is_complete else list(decision.missing_fields),
        "asked_fields": list(decision.asked_fields),
    }


def sync_dialogue_state(
    state: Any,
    *,
    decision: DialogueDecision,
    lang: str,
    is_complete: bool,
) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, Any]]]:
    confirmed_updates = list(dict.fromkeys([*decision.updated_paths, *decision.answered_this_turn]))
    state.confirmed_fact_paths = _merge_recent_paths(
        list(getattr(state, "confirmed_fact_paths", [])),
        confirmed_updates,
        limit=12,
    )
    memory = list(getattr(state, "dialogue_memory", []))
    memory.append(_build_memory_entry(decision, is_complete=is_complete))
    state.dialogue_memory = memory[-8:]
    summary = build_dialogue_summary(
        decision,
        lang=lang,
        is_complete=is_complete,
        confirmed_fact_paths=state.confirmed_fact_paths,
        memory_depth=len(state.dialogue_memory),
    )
    raw_dialogue = build_raw_dialogue(getattr(state, "history", []))
    state.dialogue_summary = summary
    return summary, raw_dialogue, list(state.dialogue_memory)
