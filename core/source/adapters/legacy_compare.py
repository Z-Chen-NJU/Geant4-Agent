from __future__ import annotations

from typing import Any

from core.contracts.slots import SlotFrame
from core.orchestrator.types import CandidateUpdate
from core.slots.slot_mapper import slot_frame_to_candidates
from core.source.adapters.diff import diff_source_config_fragment
from core.source.compiler import compile_source_spec_from_slot_frame


def legacy_source_from_candidate(candidate: CandidateUpdate | None) -> dict[str, Any]:
    source: dict[str, Any] = {}
    if candidate is None:
        return source
    for update in candidate.updates:
        if update.op != "set":
            continue
        if update.path == "source.type":
            source["type"] = update.value
        elif update.path == "source.particle":
            source["particle"] = update.value
        elif update.path == "source.energy":
            source["energy"] = update.value
        elif update.path == "source.position":
            source["position"] = update.value
        elif update.path == "source.direction":
            source["direction"] = update.value
    return source


def compare_slot_frame_source(frame: SlotFrame, *, turn_id: int) -> dict[str, Any] | None:
    if not frame.has_content():
        return None
    compile_result = compile_source_spec_from_slot_frame(frame)
    slot_candidate, _ = slot_frame_to_candidates(frame, turn_id=turn_id)
    legacy_source = legacy_source_from_candidate(slot_candidate)
    if compile_result.spec is None:
        return {
            "matches": False,
            "compile_ok": False,
            "legacy_source": legacy_source,
            "errors": list(compile_result.errors),
            "missing_fields": list(compile_result.missing_fields),
            "intent": {
                "source_type": compile_result.intent.source_type,
                "fields": dict(compile_result.intent.fields),
                "ambiguities": list(compile_result.intent.ambiguities),
            },
        }
    diff = diff_source_config_fragment(compile_result.spec, legacy_source)
    diff.update(
        {
            "compile_ok": True,
            "spec_source_type": compile_result.spec.source_type,
            "spec_confidence": compile_result.spec.confidence,
            "finalization_status": compile_result.spec.finalization_status,
        }
    )
    return diff
