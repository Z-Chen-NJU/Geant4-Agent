from __future__ import annotations

from core.orchestrator.types import CandidateUpdate


def _matches_explicit_target(path: str, target_paths: list[str]) -> bool:
    for target in target_paths:
        if not isinstance(target, str) or not target:
            continue
        if "." not in target:
            if path == target or path.startswith(target + "."):
                return True
            continue
        if path == target or path.startswith(target + "."):
            return True
    return False


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


def filter_candidate_by_explicit_targets(candidate: CandidateUpdate, target_paths: list[str]) -> CandidateUpdate:
    explicit_targets = [str(path) for path in target_paths if isinstance(path, str) and path]
    if not explicit_targets or not candidate.updates:
        return candidate
    filtered = [u for u in candidate.updates if _matches_explicit_target(u.path, explicit_targets)]
    if len(filtered) == len(candidate.updates):
        return candidate
    return CandidateUpdate(
        producer=candidate.producer,
        intent=candidate.intent,
        target_paths=sorted(set(explicit_targets) | {u.path for u in filtered}),
        updates=filtered,
        confidence=candidate.confidence,
        rationale=f"{candidate.rationale}_path_filtered",
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
