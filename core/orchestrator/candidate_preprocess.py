from __future__ import annotations

from core.orchestrator.types import CandidateUpdate


def filter_candidate_by_target_scopes(candidate: CandidateUpdate, target_paths: list[str]) -> CandidateUpdate:
    scopes = {str(p).split(".", 1)[0] for p in target_paths if "." in str(p)}
    if not scopes:
        return candidate
    filtered = [u for u in candidate.updates if u.path.split(".", 1)[0] in scopes]
    if len(filtered) == len(candidate.updates):
        return candidate
    return CandidateUpdate(
        producer=candidate.producer,
        intent=candidate.intent,
        target_paths=sorted({u.path for u in filtered}),
        updates=filtered,
        confidence=candidate.confidence,
        rationale=f"{candidate.rationale}_scope_filtered",
    )


def drop_updates_shadowed_by_anchor(candidate: CandidateUpdate, anchor: CandidateUpdate | None) -> CandidateUpdate:
    if anchor is None or not anchor.updates or not candidate.updates:
        return candidate
    anchored_paths = {upd.path for upd in anchor.updates}
    filtered = [upd for upd in candidate.updates if upd.path not in anchored_paths]
    if len(filtered) == len(candidate.updates):
        return candidate
    return CandidateUpdate(
        producer=candidate.producer,
        intent=candidate.intent,
        target_paths=sorted({u.path for u in filtered}),
        updates=filtered,
        confidence=candidate.confidence,
        rationale=f"{candidate.rationale}_anchor_shadow_filtered",
    )
