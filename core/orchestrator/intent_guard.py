from __future__ import annotations

from core.orchestrator.constraint_ledger import find_lock
from core.orchestrator.types import CandidateUpdate, Producer
from core.validation.error_codes import E_LOCKED_FIELD_OVERRIDE


def can_override_locked_field(candidate: CandidateUpdate, ledger: list, update_path: str) -> tuple[bool, str]:
    if candidate.producer != Producer.USER_EXPLICIT:
        return False, E_LOCKED_FIELD_OVERRIDE
    if candidate.intent.value not in {"SET", "MODIFY"}:
        return False, E_LOCKED_FIELD_OVERRIDE
    if not candidate.target_paths:
        return False, E_LOCKED_FIELD_OVERRIDE
    explicit_target = any(update_path == p or update_path.startswith(p + ".") for p in candidate.target_paths)
    if not explicit_target:
        return False, E_LOCKED_FIELD_OVERRIDE
    if find_lock(ledger, update_path) is None:
        return False, E_LOCKED_FIELD_OVERRIDE
    return True, ""
