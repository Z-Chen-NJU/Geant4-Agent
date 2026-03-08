from __future__ import annotations

from core.geometry.family_catalog import GEOMETRY_KIND_TO_STRUCTURE, GEOMETRY_SLOT_TARGET_TO_PATHS
from core.orchestrator.types import CandidateUpdate, Intent, Producer, UpdateOp
from core.slots.slot_frame import SlotFrame

_SLOT_TARGET_TO_PATHS = {
    **GEOMETRY_SLOT_TARGET_TO_PATHS,
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

_MATERIAL_CANONICAL_OVERRIDES = {
    "g4_csi": "G4_CESIUM_IODIDE",
    "csi": "G4_CESIUM_IODIDE",
    "cesium iodide": "G4_CESIUM_IODIDE",
    "caesium iodide": "G4_CESIUM_IODIDE",
}


def _canonical_material_name(value: str) -> str:
    text = str(value or "").strip()
    return _MATERIAL_CANONICAL_OVERRIDES.get(text.lower(), text)


def _vector3(value: list[float]) -> dict[str, object]:
    return {"type": "vector", "value": [float(value[0]), float(value[1]), float(value[2])]}


def slot_frame_to_candidates(frame: SlotFrame, *, turn_id: int) -> tuple[CandidateUpdate | None, CandidateUpdate]:
    updates: list[UpdateOp] = []
    target_paths: list[str] = []

    if frame.geometry.kind:
        structure = GEOMETRY_KIND_TO_STRUCTURE.get(frame.geometry.kind)
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

    if frame.geometry.radius1_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.rmax1",
                op="set",
                value=float(frame.geometry.radius1_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.rmax1")

    if frame.geometry.radius2_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.rmax2",
                op="set",
                value=float(frame.geometry.radius2_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.rmax2")

    if frame.geometry.x1_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.x1",
                op="set",
                value=float(frame.geometry.x1_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.x1")

    if frame.geometry.x2_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.x2",
                op="set",
                value=float(frame.geometry.x2_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.x2")

    if frame.geometry.y1_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.y1",
                op="set",
                value=float(frame.geometry.y1_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.y1")

    if frame.geometry.y2_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.y2",
                op="set",
                value=float(frame.geometry.y2_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.y2")

    if frame.geometry.z_mm is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.module_z",
                op="set",
                value=float(frame.geometry.z_mm),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.module_z")

    if frame.geometry.z_planes_mm and len(frame.geometry.z_planes_mm) == 3:
        for label, value in zip(("z1", "z2", "z3"), frame.geometry.z_planes_mm):
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

    if frame.geometry.radii_mm and len(frame.geometry.radii_mm) == 3:
        for label, value in zip(("r1", "r2", "r3"), frame.geometry.radii_mm):
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

    for slot_name, param_name in (
        ("trap_x1_mm", "trap_x1"),
        ("trap_x2_mm", "trap_x2"),
        ("trap_x3_mm", "trap_x3"),
        ("trap_x4_mm", "trap_x4"),
        ("trap_y1_mm", "trap_y1"),
        ("trap_y2_mm", "trap_y2"),
        ("trap_z_mm", "trap_z"),
        ("para_x_mm", "para_x"),
        ("para_y_mm", "para_y"),
        ("para_z_mm", "para_z"),
        ("para_alpha_deg", "para_alpha"),
        ("para_theta_deg", "para_theta"),
        ("para_phi_deg", "para_phi"),
        ("torus_major_radius_mm", "torus_rtor"),
        ("torus_minor_radius_mm", "torus_rmax"),
        ("ellipsoid_ax_mm", "ellipsoid_ax"),
        ("ellipsoid_by_mm", "ellipsoid_by"),
        ("ellipsoid_cz_mm", "ellipsoid_cz"),
        ("elltube_ax_mm", "elltube_ax"),
        ("elltube_by_mm", "elltube_by"),
        ("elltube_hz_mm", "elltube_hz"),
    ):
        value = getattr(frame.geometry, slot_name)
        if value is None:
            continue
        updates.append(
            UpdateOp(
                path=f"geometry.params.{param_name}",
                op="set",
                value=float(value),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append(f"geometry.params.{param_name}")

    if frame.geometry.polyhedra_sides is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.polyhedra_nsides",
                op="set",
                value=int(frame.geometry.polyhedra_sides),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.polyhedra_nsides")

    if frame.geometry.tilt_x_deg is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.tilt_x",
                op="set",
                value=float(frame.geometry.tilt_x_deg),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.tilt_x")

    if frame.geometry.tilt_y_deg is not None:
        updates.append(
            UpdateOp(
                path="geometry.params.tilt_y",
                op="set",
                value=float(frame.geometry.tilt_y_deg),
                producer=Producer.SLOT_MAPPER,
                confidence=frame.confidence or 0.8,
                turn_id=turn_id,
            )
        )
        target_paths.append("geometry.params.tilt_y")

    if frame.materials.primary:
        updates.append(
            UpdateOp(
                path="materials.selected_materials",
                op="set",
                value=[_canonical_material_name(frame.materials.primary)],
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
        intent=frame.intent if frame.intent in {Intent.SET, Intent.MODIFY, Intent.REMOVE, Intent.CONFIRM, Intent.REJECT, Intent.QUESTION} else Intent.OTHER,
        target_paths=list(target_paths),
        updates=[],
        confidence=frame.confidence or 0.8,
        rationale="slot_frame_user_targets",
    )
    return content_candidate, user_candidate
