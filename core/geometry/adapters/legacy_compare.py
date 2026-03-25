from __future__ import annotations

from typing import Any

from core.contracts.slots import SlotFrame
from core.geometry.adapters.diff import diff_geometry_config_fragment
from core.geometry.compiler import compile_geometry_spec_from_slot_frame
from core.orchestrator.types import CandidateUpdate
from core.slots.slot_mapper import slot_frame_to_candidates


def legacy_geometry_from_candidate(candidate: CandidateUpdate | None) -> dict[str, Any]:
    geometry: dict[str, Any] = {"params": {}}
    if candidate is None:
        return geometry
    for update in candidate.updates:
        if update.op != "set":
            continue
        if update.path == "geometry.structure":
            geometry["structure"] = update.value
            continue
        if update.path.startswith("geometry.params."):
            param_name = update.path.split(".", 2)[-1]
            geometry.setdefault("params", {})[param_name] = update.value
    return geometry


def compare_slot_frame_geometry(frame: SlotFrame, *, turn_id: int) -> dict[str, Any] | None:
    if not frame.has_content():
        return None
    compile_result = compile_geometry_spec_from_slot_frame(frame)
    slot_candidate, _ = slot_frame_to_candidates(frame, turn_id=turn_id)
    legacy_geometry = legacy_geometry_from_candidate(slot_candidate)
    if compile_result.spec is None:
        return {
            "matches": False,
            "compile_ok": False,
            "legacy_geometry": legacy_geometry,
            "errors": list(compile_result.errors),
            "missing_fields": list(compile_result.missing_fields),
            "intent": {
                "structure": compile_result.intent.structure,
                "kind": compile_result.intent.kind,
                "params": dict(compile_result.intent.params),
                "ambiguities": list(compile_result.intent.ambiguities),
            },
        }

    diff = diff_geometry_config_fragment(compile_result.spec, legacy_geometry)
    diff.update(
        {
            "compile_ok": True,
            "spec_structure": compile_result.spec.structure,
            "spec_confidence": compile_result.spec.confidence,
            "finalization_status": compile_result.spec.finalization_status,
        }
    )
    return diff

