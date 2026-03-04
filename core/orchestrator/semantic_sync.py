from __future__ import annotations

from pathlib import PurePosixPath

from core.orchestrator.path_ops import get_path
from core.orchestrator.types import CandidateUpdate, Intent, Producer, UpdateOp


def _infer_root_name(structure: str | None) -> str:
    return {
        "single_box": "box",
        "single_tubs": "tubs",
        "single_sphere": "sphere",
        "boolean": "boolean",
    }.get(str(structure or ""), "target")


def _latest_update_for_prefix(recent_updates: list[UpdateOp] | None, prefix: str) -> UpdateOp | None:
    updates = recent_updates or []
    return next((upd for upd in reversed(updates) if upd.path.startswith(prefix)), None)


def _sync_output(config: dict) -> dict[str, object]:
    fmt = get_path(config, "output.format")
    path = get_path(config, "output.path")
    if not fmt:
        return {}

    suffix_map = {
        "csv": ".csv",
        "hdf5": ".hdf5",
        "json": ".json",
        "root": ".root",
        "xml": ".xml",
    }
    expected_suffix = suffix_map.get(str(fmt).lower())
    if not expected_suffix:
        return {}

    if not path:
        return {"output.path": f"output/result{expected_suffix}"}

    raw_path = str(path).replace("\\", "/")
    if raw_path.lower().endswith(expected_suffix):
        return {}

    posix_path = PurePosixPath(raw_path)
    updated_path = f"{posix_path.with_suffix(expected_suffix)}"
    if updated_path == raw_path:
        return {}
    return {"output.path": updated_path}


def _sync_geometry(config: dict) -> dict[str, object]:
    structure = get_path(config, "geometry.structure")
    if not structure:
        return {}
    root_name = _infer_root_name(structure)
    if get_path(config, "geometry.root_name") == root_name:
        return {}
    return {"geometry.root_name": root_name}


def _sync_materials(config: dict, recent_updates: list[UpdateOp] | None) -> dict[str, object]:
    updates: dict[str, object] = {}
    structure = get_path(config, "geometry.structure")
    mats = get_path(config, "materials.selected_materials", [])
    root_name = get_path(config, "geometry.root_name") or _infer_root_name(structure)

    if structure and isinstance(mats, list) and len(mats) == 1 and mats[0]:
        expected_map = {root_name: mats[0]}
        current_map = get_path(config, "materials.volume_material_map", {})
        if current_map != expected_map:
            updates["materials.volume_material_map"] = expected_map

    if get_path(config, "materials.selection_source") is not None:
        return updates
    if not isinstance(mats, list) or not mats:
        return updates

    material_update = _latest_update_for_prefix(recent_updates, "materials.")
    source_value = "explicit_request"
    reason_value = ["Material provided explicitly by user or extracted semantics."]
    if material_update is not None and material_update.producer == Producer.RULE_DEFAULT:
        source_value = "semantic_sync"
        reason_value = ["Material assignment carried forward by deterministic semantic synchronization."]
    updates["materials.selection_source"] = source_value
    updates["materials.selection_reasons"] = reason_value
    return updates


def _sync_source(config: dict, recent_updates: list[UpdateOp] | None) -> dict[str, object]:
    updates: dict[str, object] = {}
    position = get_path(config, "source.position")
    direction = get_path(config, "source.direction")
    inferred_type = False

    if get_path(config, "source.type") is None and (position is not None or direction is not None):
        updates["source.type"] = "point"
        inferred_type = True

    if get_path(config, "source.selection_source") is not None:
        return updates

    has_source_content = any(
        get_path(config, path) is not None
        for path in (
            "source.type",
            "source.particle",
            "source.energy",
            "source.position",
            "source.direction",
        )
    ) or inferred_type
    if not has_source_content:
        return updates

    source_update = _latest_update_for_prefix(recent_updates, "source.")
    source_value = "explicit_request"
    reasons = ["Source parameters provided explicitly by user or extracted semantics."]
    if source_update is not None and source_update.producer == Producer.RULE_DEFAULT:
        source_value = "semantic_sync"
        reasons = ["Source parameters carried forward by deterministic semantic synchronization."]
    if inferred_type:
        reasons = list(reasons)
        reasons.append("Source type inferred as point because position or direction was provided.")
    updates["source.selection_source"] = source_value
    updates["source.selection_reasons"] = reasons
    return updates


def _sync_physics(config: dict, recent_updates: list[UpdateOp] | None) -> dict[str, object]:
    physics_list = get_path(config, "physics.physics_list")
    if not physics_list:
        return {}
    if get_path(config, "physics.selection_source") is not None:
        return {}

    physics_update = _latest_update_for_prefix(recent_updates, "physics.")
    if physics_update and physics_update.producer == Producer.LLM_RECOMMENDER:
        return {}

    source_value = "explicit_request"
    reason_value = ["Physics list provided explicitly by user or extracted semantics."]
    if physics_update is not None and physics_update.producer == Producer.RULE_DEFAULT:
        source_value = "semantic_sync"
        reason_value = ["Physics list carried forward by deterministic semantic synchronization."]
    return {
        "physics.selection_source": source_value,
        "physics.selection_reasons": reason_value,
    }


def build_semantic_sync_candidate(
    config: dict,
    *,
    turn_id: int,
    recent_updates: list[UpdateOp] | None = None,
) -> CandidateUpdate | None:
    updates: dict[str, object] = {}
    updates.update(_sync_output(config))
    updates.update(_sync_source(config, recent_updates))
    updates.update(_sync_geometry(config))
    updates.update(_sync_materials(config, recent_updates))
    updates.update(_sync_physics(config, recent_updates))

    if not updates:
        return None

    ordered_paths = [
        path_name
        for path_name in (
            "source.type",
            "source.selection_source",
            "source.selection_reasons",
            "output.path",
            "geometry.root_name",
            "materials.volume_material_map",
            "materials.selection_source",
            "materials.selection_reasons",
            "physics.selection_source",
            "physics.selection_reasons",
        )
        if path_name in updates
    ]

    return CandidateUpdate(
        producer=Producer.RULE_DEFAULT,
        intent=Intent.SET,
        target_paths=ordered_paths,
        updates=[
            UpdateOp(
                path=path_name,
                op="set",
                value=updates[path_name],
                producer=Producer.RULE_DEFAULT,
                confidence=1.0,
                turn_id=turn_id,
            )
            for path_name in ordered_paths
        ],
        confidence=1.0,
        rationale="semantic_sync",
    )
