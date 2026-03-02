from __future__ import annotations

from dataclasses import dataclass

from core.orchestrator.path_ops import deep_copy
from core.orchestrator.types import ConstraintItem, Phase, SessionState


@dataclass
class TurnDraft:
    config: dict
    constraint_ledger: list[ConstraintItem]
    field_sources: dict[str, str]
    phase: Phase


def begin_turn(state: SessionState) -> TurnDraft:
    return TurnDraft(
        config=deep_copy(state.config),
        constraint_ledger=deep_copy(state.constraint_ledger),
        field_sources=deep_copy(state.field_sources),
        phase=state.phase,
    )


def commit_turn(state: SessionState, draft: TurnDraft) -> None:
    state.config = draft.config
    state.constraint_ledger = draft.constraint_ledger
    state.field_sources = draft.field_sources
    state.phase = draft.phase

