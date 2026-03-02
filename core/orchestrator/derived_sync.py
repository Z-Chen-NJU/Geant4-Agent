from __future__ import annotations

from core.orchestrator.semantic_sync import build_semantic_sync_candidate


def build_derived_sync_candidate(*args, **kwargs):
    return build_semantic_sync_candidate(*args, **kwargs)
