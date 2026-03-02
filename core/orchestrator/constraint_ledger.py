from __future__ import annotations

from core.orchestrator.path_ops import get_path
from core.orchestrator.types import CandidateUpdate, ConstraintItem, LockReason, Producer, Scope


def path_matches(lock_path: str, scope: Scope, target_path: str) -> bool:
    if scope == Scope.EXACT:
        return lock_path == target_path
    return target_path == lock_path or target_path.startswith(lock_path + ".")


def find_lock(ledger: list[ConstraintItem], path: str) -> ConstraintItem | None:
    for item in reversed(ledger):
        if not item.locked:
            continue
        if path_matches(item.path, item.scope, path):
            return item
    return None


def upsert_lock(
    ledger: list[ConstraintItem],
    path: str,
    value: object,
    turn_id: int,
    reason_code: LockReason,
    source: str = "user",
    scope: Scope = Scope.EXACT,
) -> None:
    for item in reversed(ledger):
        if item.path == path and item.scope == scope:
            item.value = value
            item.locked = True
            item.reason_code = reason_code
            item.source = source
            item.turn_id = turn_id
            return
    ledger.append(
        ConstraintItem(
            path=path,
            value=value,
            locked=True,
            reason_code=reason_code,
            scope=scope,
            source=source,
            turn_id=turn_id,
        )
    )


def lock_from_candidate(
    ledger: list[ConstraintItem],
    candidate: CandidateUpdate,
    config: dict,
    turn_id: int,
) -> None:
    if candidate.producer != Producer.USER_EXPLICIT:
        return
    if candidate.intent.value not in {"SET", "MODIFY"}:
        return
    targets = candidate.target_paths or [u.path for u in candidate.updates]
    for path in targets:
        value = get_path(config, path)
        if value is None:
            continue
        upsert_lock(
            ledger=ledger,
            path=path,
            value=value,
            turn_id=turn_id,
            reason_code=LockReason.USER_EXPLICIT,
            source="user_explicit",
            scope=Scope.EXACT,
        )
