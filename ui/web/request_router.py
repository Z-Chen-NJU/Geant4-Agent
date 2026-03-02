from __future__ import annotations

from typing import Any, Callable

from ui.web.runtime_state import runtime_config_payload, set_ollama_config_path
from ui.web.strict_api import handle_strict_audit, handle_strict_reset


POST_PATHS = {"/api/solve", "/api/step", "/api/reset", "/api/runtime", "/api/audit"}


def is_supported_post_path(path: str) -> bool:
    return path in POST_PATHS


def handle_post_request(
    path: str,
    payload: dict[str, Any],
    *,
    legacy_sessions: dict[str, Any],
    solve_fn: Callable[[dict[str, Any]], dict[str, Any]],
    step_fn: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    if path == "/api/solve":
        return 200, solve_fn(payload)

    if path == "/api/reset":
        session_id = payload.get("session_id")
        if session_id in legacy_sessions:
            del legacy_sessions[session_id]
        handle_strict_reset(str(session_id) if session_id else None)
        return 200, {"ok": True}

    if path == "/api/audit":
        session_id = str(payload.get("session_id", "")).strip()
        return 200, {"session_id": session_id, "audit": handle_strict_audit(session_id)}

    if path == "/api/runtime":
        cfg_path = str(payload.get("ollama_config_path", "")).strip()
        ok, message = set_ollama_config_path(cfg_path)
        body = {"ok": ok, "message": message, **runtime_config_payload()}
        return (200 if ok else 400), body

    return 200, step_fn(payload)
