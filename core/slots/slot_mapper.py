from __future__ import annotations

from core.orchestrator.types import CandidateUpdate, Intent, Producer, UpdateOp
from core.slots.slot_frame import SlotFrame


_GEOMETRY_KIND_TO_STRUCTURE = {
    "box": "single_box",
    "cylinder": "single_tubs",
    "sphere": "single_sphere",
}

_SLOT_TARGET_TO_PATHS = {
    "geometry.kind": {"geometry.structure", "geometry.root_name"},
    "geometry.size_triplet_mm": {
        "geometry.params.module_x",
        "geometry.params.module_y",
        "geometry.params.module_z",
    },
    "geometry.radius_mm": {"geometry.params.child_rmax"},
    "geometry.half_length_mm": {"geometry.params.child_hz"},
    "materials.primary": {"materials.selected_materials", "materials.volume_material_map"},
    "source.kind": {"source.type"},
    "source.particle": {"source.particle"},
    "source.energy_mev": {"source.energy"},
    "source.position_mm": {"source.position"},
    "source.direction_vec": {"source.direction"},
    "physics.explicit_list": {"physics.physics_list"},
    "physics.recommendation_intent": {"physics.physics_list"},
    "output.format": {"output.format", "output.path"},
    "output.path": {"output.path"},
}


def _vector3(value: list[float]) -> dict[str, object]:
    return {"type": "vector", "value": [float(value[0]), float(value[1]), float(value[2])]}


def slot_frame_to_candidates(frame: SlotFrame, *, turn_id: int) -> tuple[CandidateUpdate | None, CandidateUpdate]:
    updates: list[UpdateOp] = []
    target_paths: list[str] = []

    if frame.geometry.kind:
        structure = _GEOMETRY_KIND_TO_STRUCTURE.get(frame.geometry.kind)
        if structure:
            updates.append(
                UpdateOp(
                    path="geometry.structure",
                    op="set",
                    value=structure,
                    producer=Producer.SLOT_MAPPER,
                    confidence=frame.confidence or 0.8,
                    turn_id=turn_id,
                )
            )
            target_paths.extend(["geometry.structure", "geometry.root_name"])

    if frame.geometry.size_triplet_mm:
        labels = ("module_x", "module_y", "module_z")
        for label, value in zip(labels, frame.geometry.size_triplet_mm):
            updates.append(
                UpdateOp(
                    path=f"geometry.params.{label}",
                    op="set",
                    value=float(value),
                    producer=Producer.SLOT_MAPPER,
                    confidence=frame.confidence or 0.8,
                    turn_id=turn_id,
                )
            )
            target_paths.append(f"geometry.params.{label}")

    if frame.geometry.radius_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.child_rmax",
                op="set",
                value=float(frame.geometry.radius_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.child_rmax")

    if frame.geometry.half_length_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.child_hz",
                op="set",
                value=float(frame.geometry.half_length_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.child_hz")

    if frame.materials.primary:
        updates.append(
            UpdateOp(
                path="materials.selected_materials",
                op="set",
                value=[frame.materials.primary],
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.extend(["materials.selected_materials", "materials.volume_material_map"])

    if frame.source.kind:
        updates.append(
            UpdateOp(
                path="source.type",
                op="set",
                value=frame.source.kind,
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("source.type")

    if frame.source.particle:
        updates.append(
            UpdateOp(
                path="source.particle",
                op="set",
                value=frame.source.particle,
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("source.particle")

    if frame.source.energy_mev is not None:
        updates.append(
            UpdateOp(
                path="source.energy",
                op="set",
                value=float(frame.source.energy_mev),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("source.energy")

    if frame.source.position_mm:
        updates.append(
            UpdateOp(
                path="source.position",
                op="set",
                value=_vector3(frame.source.position_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("source.position")

    if frame.source.direction_vec:
        updates.append(
            UpdateOp(
                path="source.direction",
                op="set",
                value=_vector3(frame.source.direction_vec),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("source.direction")

    if frame.physics.explicit_list:
        updates.append(
            UpdateOp(
                path="physics.physics_list",
                op="set",
                value=frame.physics.explicit_list,
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("physics.physics_list")

    if frame.output.format:
        updates.append(
            UpdateOp(
                path="output.format",
                op="set",
                value=frame.output.format,
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.extend(["output.format", "output.path"])

    if frame.output.path:
        updates.append(
            UpdateOp(
                path="output.path",
                op="set",
                value=frame.output.path,
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("output.path")

    dedup_updates: dict[str, UpdateOp] = {}
    for update in updates:
        dedup_updates[update.path] = update
    updates = list(dedup_updates.values())
    for slot_target in frame.target_slots:
        target_paths.extend(_SLOT_TARGET_TO_PATHS.get(slot_target, set()))
    target_paths = sorted(set(target_paths) | {u.path for u in updates})

    content_candidate = None
    if updates:
        content_candidate = CandidateUpdate(
            producer=Producer.SLOT_MAPPER,
            intent=frame.intent,
            target_paths=list(target_paths),
            updates=updates,
            confidence=frame.confidence or 0.8,
            rationale="slot_frame_mapper",
        )

    user_candidate = CandidateUpdate(
        producer=Producer.USER_EXPLICIT,
        intent=frame.intent if frame.intent in {Intent.SET, Intent.MODIFY, Intent.REMOVE, Intent.CONFIRM, Intent.QUESTION} else Intent.OTHER,
        target_paths=list(target_paths),
        updates=[],
        confidence=frame.confidence or 0.8,
        rationale="slot_frame_user_targets",
    )
    return content_candidate, user_candidate
