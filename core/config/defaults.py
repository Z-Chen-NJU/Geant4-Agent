from __future__ import annotations

from typing import Any


def geometry_block(*, strict: bool) -> dict[str, Any]:
    block: dict[str, Any] = {
        "structure": None,
        "params": {},
        "feasible": None,
    }
    if strict:
        block["root_name"] = None
    else:
        block.update(
            {
                "graph_program": None,
                "chosen_skeleton": None,
                "dsl": None,
                "errors": [],
            }
        )
    return block


def materials_block() -> dict[str, Any]:
    return {
        "selected_materials": [],
        "volume_material_map": {},
        "selection_source": None,
        "selection_reasons": [],
    }


def source_block() -> dict[str, Any]:
    return {
        "type": None,
        "particle": None,
        "energy": None,
        "position": None,
        "direction": None,
        "selection_source": None,
        "selection_reasons": [],
    }


def physics_block() -> dict[str, Any]:
    return {
        "physics_list": None,
        "backup_physics_list": None,
        "selection_reasons": [],
        "covered_processes": [],
        "selection_source": None,
    }


def output_block() -> dict[str, Any]:
    return {
        "format": None,
        "path": None,
    }


def build_strict_default_config() -> dict[str, Any]:
    return {
        "geometry": geometry_block(strict=True),
        "materials": materials_block(),
        "source": source_block(),
        "physics": physics_block(),
        "output": output_block(),
    }


def build_legacy_default_config() -> dict[str, Any]:
    return {
        "geometry": geometry_block(strict=False),
        "materials": materials_block(),
        "source": source_block(),
        "physics": physics_block(),
        "environment": {
            "temperature": None,
            "pressure": None,
        },
        "output": output_block(),
        "notes": [],
    }

