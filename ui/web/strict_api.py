from __future__ import annotations

from core.orchestrator.session_manager import (
    get_session_audit as get_session_audit_v2,
    process_turn as process_turn_v2,
    reset_session as reset_session_v2,
)

from ui.web.runtime_state import get_ollama_config_path


def handle_strict_step(payload: dict) -> dict:
    return process_turn_v2(
        payload=payload,
        ollama_config_path=get_ollama_config_path(),
        min_confidence=float(payload.get("min_confidence", 0.6)),
        lang=str(payload.get("lang", "zh")).lower(),
    )


def handle_strict_reset(session_id: str | None) -> None:
    if session_id:
        reset_session_v2(str(session_id))


def handle_strict_audit(session_id: str) -> list[dict]:
    return get_session_audit_v2(session_id)

