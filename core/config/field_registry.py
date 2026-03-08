from __future__ import annotations

from core.config.path_registry import canonical_field_path
from core.config.prompt_registry import completion_message, single_field_request


_FRIENDLY = {
    "en": {
        "geometry.structure": "geometry structure",
        "geometry.root_name": "geometry root volume",
        "geometry.ask.ring.module_size": "ring module size",
        "geometry.ask.ring.count": "ring module count",
        "geometry.ask.ring.radius": "ring radius",
        "geometry.ask.ring.clearance": "ring clearance",
        "geometry.ask.grid.module_size": "grid module size",
        "geometry.ask.grid.count_x": "grid module count along x",
        "geometry.ask.grid.count_y": "grid module count along y",
        "geometry.ask.grid.pitch_x": "grid pitch along x",
        "geometry.ask.grid.pitch_y": "grid pitch along y",
        "geometry.ask.grid.clearance": "grid clearance",
        "geometry.ask.nest.parent_size": "container size",
        "geometry.ask.nest.child_radius": "nested cylinder radius",
        "geometry.ask.nest.child_half_length": "nested cylinder half length",
        "geometry.ask.nest.clearance": "nest clearance",
        "geometry.ask.stack.footprint": "stack layer footprint",
        "geometry.ask.stack.thicknesses": "stack layer thicknesses",
        "geometry.ask.stack.layer_clearance": "stack layer clearance",
        "geometry.ask.stack.parent_size": "stack container size",
        "geometry.ask.stack.nest_clearance": "stack container clearance",
        "geometry.ask.shell.inner_radius": "shell inner radius",
        "geometry.ask.shell.thicknesses": "shell thicknesses",
        "geometry.ask.shell.half_length": "shell half length",
        "geometry.ask.shell.child_radius": "nested core radius",
        "geometry.ask.shell.child_half_length": "nested core half length",
        "geometry.ask.shell.clearance": "shell clearance",
        "geometry.ask.boolean.solid_a_size": "boolean solid A size",
        "geometry.ask.boolean.solid_b_size": "boolean solid B size",
        "materials.selected_materials": "selected materials",
        "materials.volume_material_map": "volume-to-material binding",
        "materials.selection_source": "material selection source",
        "materials.selection_reasons": "material selection reasons",
        "source.type": "source type",
        "source.particle": "particle type",
        "source.energy": "source energy",
        "source.position": "source position",
        "source.direction": "source direction",
        "source.selection_source": "source selection source",
        "source.selection_reasons": "source selection reasons",
        "physics.physics_list": "physics list",
        "physics.backup_physics_list": "backup physics list",
        "physics.selection_source": "physics selection source",
        "physics.selection_reasons": "physics selection reasons",
        "output.format": "output format",
        "output.path": "output path",
    },
    "zh": {
        "geometry.structure": "\u51e0\u4f55\u7ed3\u6784\u7c7b\u578b",
        "geometry.root_name": "\u51e0\u4f55\u6839\u4f53\u79ef\u540d",
        "geometry.ask.ring.module_size": "\u73af\u5f62\u6a21\u5757\u5c3a\u5bf8",
        "geometry.ask.ring.count": "\u73af\u5f62\u6a21\u5757\u6570\u91cf",
        "geometry.ask.ring.radius": "\u73af\u5f62\u534a\u5f84",
        "geometry.ask.ring.clearance": "\u73af\u5f62\u95f4\u9699",
        "geometry.ask.grid.module_size": "\u9635\u5217\u6a21\u5757\u5c3a\u5bf8",
        "geometry.ask.grid.count_x": "x \u65b9\u5411\u9635\u5217\u6570\u91cf",
        "geometry.ask.grid.count_y": "y \u65b9\u5411\u9635\u5217\u6570\u91cf",
        "geometry.ask.grid.pitch_x": "x \u65b9\u5411 pitch",
        "geometry.ask.grid.pitch_y": "y \u65b9\u5411 pitch",
        "geometry.ask.grid.clearance": "\u9635\u5217\u95f4\u9699",
        "geometry.ask.nest.parent_size": "\u5916\u5c42\u5bb9\u5668\u5c3a\u5bf8",
        "geometry.ask.nest.child_radius": "\u5185\u5d4c\u5706\u67f1\u534a\u5f84",
        "geometry.ask.nest.child_half_length": "\u5185\u5d4c\u5706\u67f1\u534a\u957f",
        "geometry.ask.nest.clearance": "\u5d4c\u5957\u95f4\u9699",
        "geometry.ask.stack.footprint": "\u5806\u53e0\u5c42\u9762\u79ef\u5c3a\u5bf8",
        "geometry.ask.stack.thicknesses": "\u5806\u53e0\u5c42\u539a\u5ea6",
        "geometry.ask.stack.layer_clearance": "\u5c42\u95f4\u95f4\u9699",
        "geometry.ask.stack.parent_size": "\u5806\u53e0\u5916\u76d2\u5c3a\u5bf8",
        "geometry.ask.stack.nest_clearance": "\u5806\u53e0\u5916\u76d2\u95f4\u9699",
        "geometry.ask.shell.inner_radius": "\u58f3\u5c42\u5185\u534a\u5f84",
        "geometry.ask.shell.thicknesses": "\u58f3\u5c42\u539a\u5ea6",
        "geometry.ask.shell.half_length": "\u58f3\u5c42\u534a\u957f",
        "geometry.ask.shell.child_radius": "\u5185\u6838\u534a\u5f84",
        "geometry.ask.shell.child_half_length": "\u5185\u6838\u534a\u957f",
        "geometry.ask.shell.clearance": "\u58f3\u5c42\u95f4\u9699",
        "geometry.ask.boolean.solid_a_size": "\u5e03\u5c14 solid A \u5c3a\u5bf8",
        "geometry.ask.boolean.solid_b_size": "\u5e03\u5c14 solid B \u5c3a\u5bf8",
        "materials.selected_materials": "\u5df2\u9009\u6750\u6599",
        "materials.volume_material_map": "\u4f53\u79ef\u4e0e\u6750\u6599\u7ed1\u5b9a",
        "materials.selection_source": "\u6750\u6599\u9009\u62e9\u6765\u6e90",
        "materials.selection_reasons": "\u6750\u6599\u9009\u62e9\u4f9d\u636e",
        "source.type": "\u6e90\u7c7b\u578b",
        "source.particle": "\u7c92\u5b50\u7c7b\u578b",
        "source.energy": "\u6e90\u80fd\u91cf",
        "source.position": "\u6e90\u4f4d\u7f6e",
        "source.direction": "\u6e90\u65b9\u5411",
        "source.selection_source": "\u6e90\u9009\u62e9\u6765\u6e90",
        "source.selection_reasons": "\u6e90\u9009\u62e9\u4f9d\u636e",
        "physics.physics_list": "\u7269\u7406\u5217\u8868",
        "physics.backup_physics_list": "\u5907\u9009\u7269\u7406\u5217\u8868",
        "physics.selection_source": "\u7269\u7406\u5217\u8868\u9009\u62e9\u6765\u6e90",
        "physics.selection_reasons": "\u7269\u7406\u5217\u8868\u9009\u62e9\u4f9d\u636e",
        "output.format": "\u8f93\u51fa\u683c\u5f0f",
        "output.path": "\u8f93\u51fa\u8def\u5f84",
    },
}

_QUESTION = {
    "en": {
        "physics.physics_list": "Please provide the physics list name (for example FTFP_BERT or QBBC).",
        "source.energy": "Please provide the source energy in MeV.",
        "source.position": "Please provide the source position vector as (x, y, z).",
        "source.direction": "Please provide the source direction vector as (dx, dy, dz).",
        "materials.volume_material_map": "Please confirm the volume-to-material binding (volume -> material).",
        "geometry.structure": "Please confirm the geometry shape, for example box, cylinder, sphere, ring, or stacked layers.",
        "geometry.ask.ring.module_size": "Please provide the ring module size as x, y, z.",
        "geometry.ask.ring.count": "Please provide the number of modules in the ring.",
        "geometry.ask.ring.radius": "Please provide the ring radius.",
        "geometry.ask.ring.clearance": "Please provide the clearance between neighboring ring modules.",
        "geometry.ask.grid.module_size": "Please provide the grid module size as x, y, z.",
        "geometry.ask.grid.count_x": "Please provide the grid count along x.",
        "geometry.ask.grid.count_y": "Please provide the grid count along y.",
        "geometry.ask.grid.pitch_x": "Please provide the grid pitch along x.",
        "geometry.ask.grid.pitch_y": "Please provide the grid pitch along y.",
        "geometry.ask.grid.clearance": "Please provide the clearance between neighboring grid modules.",
        "geometry.ask.nest.parent_size": "Please provide the container box size as x, y, z.",
        "geometry.ask.nest.child_radius": "Please provide the nested cylinder radius.",
        "geometry.ask.nest.child_half_length": "Please provide the nested cylinder half length.",
        "geometry.ask.nest.clearance": "Please provide the nesting clearance.",
        "geometry.ask.stack.footprint": "Please provide the stack layer footprint as x and y.",
        "geometry.ask.stack.thicknesses": "Please provide the stack layer thicknesses.",
        "geometry.ask.stack.layer_clearance": "Please provide the clearance between stacked layers.",
        "geometry.ask.stack.parent_size": "Please provide the container box size for the stack.",
        "geometry.ask.stack.nest_clearance": "Please provide the clearance between the stack and its container.",
        "geometry.ask.shell.inner_radius": "Please provide the shell inner radius.",
        "geometry.ask.shell.thicknesses": "Please provide the shell thicknesses.",
        "geometry.ask.shell.half_length": "Please provide the shell half length.",
        "geometry.ask.shell.child_radius": "Please provide the nested core radius.",
        "geometry.ask.shell.child_half_length": "Please provide the nested core half length.",
        "geometry.ask.shell.clearance": "Please provide the shell clearance.",
        "geometry.ask.boolean.solid_a_size": "Please provide the size of boolean solid A as x, y, z.",
        "geometry.ask.boolean.solid_b_size": "Please provide the size of boolean solid B as x, y, z.",
    },
    "zh": {
        "physics.physics_list": "\u8bf7\u63d0\u4f9b\u7269\u7406\u5217\u8868\u540d\u79f0\uff08\u4f8b\u5982 FTFP_BERT \u6216 QBBC\uff09\u3002",
        "source.energy": "\u8bf7\u63d0\u4f9b\u6e90\u80fd\u91cf\uff08\u5355\u4f4d\uff1aMeV\uff09\u3002",
        "source.position": "\u8bf7\u63d0\u4f9b\u6e90\u4f4d\u7f6e\u5411\u91cf\uff08x, y, z\uff09\u3002",
        "source.direction": "\u8bf7\u63d0\u4f9b\u6e90\u65b9\u5411\u5411\u91cf\uff08dx, dy, dz\uff09\u3002",
        "materials.volume_material_map": "\u8bf7\u786e\u8ba4\u4f53\u79ef\u5230\u6750\u6599\u7684\u7ed1\u5b9a\u5173\u7cfb\uff08volume -> material\uff09\u3002",
        "geometry.structure": "\u8bf7\u786e\u8ba4\u51e0\u4f55\u5f62\u72b6\uff0c\u4f8b\u5982\u76d2\u4f53\u3001\u5706\u67f1\u3001\u7403\u4f53\u3001\u73af\u5f62\u9635\u5217\u6216\u5806\u53e0\u7ed3\u6784\u3002",
        "geometry.ask.ring.module_size": "\u8bf7\u63d0\u4f9b\u73af\u5f62\u6a21\u5757\u7684 x\u3001y\u3001z \u5c3a\u5bf8\u3002",
        "geometry.ask.ring.count": "\u8bf7\u63d0\u4f9b\u73af\u5f62\u6a21\u5757\u7684\u6570\u91cf\u3002",
        "geometry.ask.ring.radius": "\u8bf7\u63d0\u4f9b\u73af\u5f62\u534a\u5f84\u3002",
        "geometry.ask.ring.clearance": "\u8bf7\u63d0\u4f9b\u73af\u5f62\u6a21\u5757\u4e4b\u95f4\u7684\u95f4\u9699\u3002",
        "geometry.ask.grid.module_size": "\u8bf7\u63d0\u4f9b\u9635\u5217\u6a21\u5757\u7684 x\u3001y\u3001z \u5c3a\u5bf8\u3002",
        "geometry.ask.grid.count_x": "\u8bf7\u63d0\u4f9b x \u65b9\u5411\u7684\u9635\u5217\u6570\u91cf\u3002",
        "geometry.ask.grid.count_y": "\u8bf7\u63d0\u4f9b y \u65b9\u5411\u7684\u9635\u5217\u6570\u91cf\u3002",
        "geometry.ask.grid.pitch_x": "\u8bf7\u63d0\u4f9b x \u65b9\u5411\u7684 pitch\u3002",
        "geometry.ask.grid.pitch_y": "\u8bf7\u63d0\u4f9b y \u65b9\u5411\u7684 pitch\u3002",
        "geometry.ask.grid.clearance": "\u8bf7\u63d0\u4f9b\u9635\u5217\u6a21\u5757\u4e4b\u95f4\u7684\u95f4\u9699\u3002",
        "geometry.ask.nest.parent_size": "\u8bf7\u63d0\u4f9b\u5916\u5c42\u76d2\u4f53\u7684 x\u3001y\u3001z \u5c3a\u5bf8\u3002",
        "geometry.ask.nest.child_radius": "\u8bf7\u63d0\u4f9b\u5185\u5d4c\u5706\u67f1\u7684\u534a\u5f84\u3002",
        "geometry.ask.nest.child_half_length": "\u8bf7\u63d0\u4f9b\u5185\u5d4c\u5706\u67f1\u7684\u534a\u957f\u3002",
        "geometry.ask.nest.clearance": "\u8bf7\u63d0\u4f9b\u5d4c\u5957\u95f4\u9699\u3002",
        "geometry.ask.stack.footprint": "\u8bf7\u63d0\u4f9b\u5806\u53e0\u5c42\u7684 x\u3001y \u5c3a\u5bf8\u3002",
        "geometry.ask.stack.thicknesses": "\u8bf7\u63d0\u4f9b\u5806\u53e0\u5c42\u7684\u5404\u5c42\u539a\u5ea6\u3002",
        "geometry.ask.stack.layer_clearance": "\u8bf7\u63d0\u4f9b\u5c42\u4e0e\u5c42\u4e4b\u95f4\u7684\u95f4\u9699\u3002",
        "geometry.ask.stack.parent_size": "\u8bf7\u63d0\u4f9b\u5806\u53e0\u5916\u76d2\u7684 x\u3001y\u3001z \u5c3a\u5bf8\u3002",
        "geometry.ask.stack.nest_clearance": "\u8bf7\u63d0\u4f9b\u5806\u53e0\u4e0e\u5916\u76d2\u4e4b\u95f4\u7684\u95f4\u9699\u3002",
        "geometry.ask.shell.inner_radius": "\u8bf7\u63d0\u4f9b\u58f3\u5c42\u7684\u5185\u534a\u5f84\u3002",
        "geometry.ask.shell.thicknesses": "\u8bf7\u63d0\u4f9b\u58f3\u5c42\u7684\u5404\u5c42\u539a\u5ea6\u3002",
        "geometry.ask.shell.half_length": "\u8bf7\u63d0\u4f9b\u58f3\u5c42\u7684\u534a\u957f\u3002",
        "geometry.ask.shell.child_radius": "\u8bf7\u63d0\u4f9b\u5185\u6838\u7684\u534a\u5f84\u3002",
        "geometry.ask.shell.child_half_length": "\u8bf7\u63d0\u4f9b\u5185\u6838\u7684\u534a\u957f\u3002",
        "geometry.ask.shell.clearance": "\u8bf7\u63d0\u4f9b\u58f3\u5c42\u95f4\u9699\u3002",
        "geometry.ask.boolean.solid_a_size": "\u8bf7\u63d0\u4f9b boolean \u7b2c\u4e00\u4e2a solid \u7684 x\u3001y\u3001z \u5c3a\u5bf8\u3002",
        "geometry.ask.boolean.solid_b_size": "\u8bf7\u63d0\u4f9b boolean \u7b2c\u4e8c\u4e2a solid \u7684 x\u3001y\u3001z \u5c3a\u5bf8\u3002",
    },
}

_GEOMETRY_PARAM = {
    "en": "geometry parameter",
    "zh": "\u51e0\u4f55\u53c2\u6570",
}

_GEOMETRY_PARAM_LABELS = {
    "en": {
        "module_x": "box size along x",
        "module_y": "box size along y",
        "module_z": "box size along z",
        "child_rmax": "radius",
        "child_hz": "half length",
        "inner_r": "inner radius",
        "hz": "half length",
        "radius": "radius",
        "n": "module count",
        "nx": "count along x",
        "ny": "count along y",
        "pitch_x": "pitch along x",
        "pitch_y": "pitch along y",
        "tilt_x": "tilt along x",
        "tilt_y": "tilt along y",
        "stack_x": "stack footprint along x",
        "stack_y": "stack footprint along y",
        "t1": "layer 1 thickness",
        "t2": "layer 2 thickness",
        "t3": "layer 3 thickness",
        "bool_a_x": "boolean solid A size along x",
        "bool_a_y": "boolean solid A size along y",
        "bool_a_z": "boolean solid A size along z",
        "bool_b_x": "boolean solid B size along x",
        "bool_b_y": "boolean solid B size along y",
        "bool_b_z": "boolean solid B size along z",
        "torus_rtor": "torus major radius",
        "torus_rmax": "torus tube radius",
        "ellipsoid_ax": "ellipsoid semi-axis a",
        "ellipsoid_by": "ellipsoid semi-axis b",
        "ellipsoid_cz": "ellipsoid semi-axis c",
        "elltube_ax": "elliptical tube semi-axis a",
        "elltube_by": "elliptical tube semi-axis b",
        "elltube_hz": "elliptical tube half length",
        "polyhedra_nsides": "polyhedra side count",
    },
    "zh": {
        "module_x": "\u76d2\u4f53 x \u65b9\u5411\u5c3a\u5bf8",
        "module_y": "\u76d2\u4f53 y \u65b9\u5411\u5c3a\u5bf8",
        "module_z": "\u76d2\u4f53 z \u65b9\u5411\u5c3a\u5bf8",
        "child_rmax": "\u534a\u5f84",
        "child_hz": "\u534a\u957f",
        "inner_r": "\u5185\u534a\u5f84",
        "hz": "\u534a\u957f",
        "radius": "\u534a\u5f84",
        "n": "\u6a21\u5757\u6570\u91cf",
        "nx": "x \u65b9\u5411\u6570\u91cf",
        "ny": "y \u65b9\u5411\u6570\u91cf",
        "pitch_x": "x \u65b9\u5411 pitch",
        "pitch_y": "y \u65b9\u5411 pitch",
        "tilt_x": "x \u65b9\u5411\u503e\u89d2",
        "tilt_y": "y \u65b9\u5411\u503e\u89d2",
        "stack_x": "\u5806\u53e0\u5360\u5730 x \u5c3a\u5bf8",
        "stack_y": "\u5806\u53e0\u5360\u5730 y \u5c3a\u5bf8",
        "t1": "\u7b2c 1 \u5c42\u539a\u5ea6",
        "t2": "\u7b2c 2 \u5c42\u539a\u5ea6",
        "t3": "\u7b2c 3 \u5c42\u539a\u5ea6",
        "bool_a_x": "boolean solid A \u7684 x \u5c3a\u5bf8",
        "bool_a_y": "boolean solid A \u7684 y \u5c3a\u5bf8",
        "bool_a_z": "boolean solid A \u7684 z \u5c3a\u5bf8",
        "bool_b_x": "boolean solid B \u7684 x \u5c3a\u5bf8",
        "bool_b_y": "boolean solid B \u7684 y \u5c3a\u5bf8",
        "bool_b_z": "boolean solid B \u7684 z \u5c3a\u5bf8",
        "torus_rtor": "\u73af\u9762\u4e3b\u534a\u5f84",
        "torus_rmax": "\u73af\u9762\u7ba1\u534a\u5f84",
        "ellipsoid_ax": "\u692d\u7403 a \u534a\u8f74",
        "ellipsoid_by": "\u692d\u7403 b \u534a\u8f74",
        "ellipsoid_cz": "\u692d\u7403 c \u534a\u8f74",
        "elltube_ax": "\u692d\u5706\u7ba1 a \u534a\u8f74",
        "elltube_by": "\u692d\u5706\u7ba1 b \u534a\u8f74",
        "elltube_hz": "\u692d\u5706\u7ba1\u534a\u957f",
        "polyhedra_nsides": "\u591a\u8fb9\u4f53\u8fb9\u6570",
    },
}


def _humanize_param_key(key: str, lang: str) -> str:
    lang_key = normalize_lang(lang)
    mapped = _GEOMETRY_PARAM_LABELS[lang_key].get(key)
    if mapped:
        return mapped
    if key.startswith("trap_"):
        suffix = key.split("_", 1)[1]
        return f"trap parameter {suffix}" if lang_key == "en" else f"Trap \u53c2\u6570 {suffix}"
    if key.startswith("para_"):
        suffix = key.split("_", 1)[1]
        return f"para parameter {suffix}" if lang_key == "en" else f"Para \u53c2\u6570 {suffix}"
    if key.endswith("_x"):
        base = key[:-2].replace("_", " ")
        return f"{base} along x" if lang_key == "en" else f"{base} \u7684 x \u65b9\u5411"
    if key.endswith("_y"):
        base = key[:-2].replace("_", " ")
        return f"{base} along y" if lang_key == "en" else f"{base} \u7684 y \u65b9\u5411"
    if key.endswith("_z"):
        base = key[:-2].replace("_", " ")
        return f"{base} along z" if lang_key == "en" else f"{base} \u7684 z \u65b9\u5411"
    return key.replace("_", " ")

_CLARIFICATION = {
    "en": {
        "geometry.structure": "geometry shape (for example box, cylinder, sphere, ring, or stack)",
        "geometry.ask.ring.module_size": "ring module size (x, y, z)",
        "geometry.ask.ring.count": "number of ring modules",
        "geometry.ask.ring.radius": "ring radius",
        "geometry.ask.ring.clearance": "ring clearance",
        "geometry.ask.grid.module_size": "grid module size (x, y, z)",
        "geometry.ask.grid.count_x": "grid count along x",
        "geometry.ask.grid.count_y": "grid count along y",
        "geometry.ask.grid.pitch_x": "grid pitch along x",
        "geometry.ask.grid.pitch_y": "grid pitch along y",
        "geometry.ask.grid.clearance": "grid clearance",
        "geometry.ask.nest.parent_size": "container box size (x, y, z)",
        "geometry.ask.nest.child_radius": "nested cylinder radius",
        "geometry.ask.nest.child_half_length": "nested cylinder half length",
        "geometry.ask.nest.clearance": "nest clearance",
        "geometry.ask.stack.footprint": "stack layer footprint (x, y)",
        "geometry.ask.stack.thicknesses": "stack layer thicknesses",
        "geometry.ask.stack.layer_clearance": "clearance between stacked layers",
        "geometry.ask.stack.parent_size": "stack container size",
        "geometry.ask.stack.nest_clearance": "stack container clearance",
        "geometry.ask.shell.inner_radius": "shell inner radius",
        "geometry.ask.shell.thicknesses": "shell thicknesses",
        "geometry.ask.shell.half_length": "shell half length",
        "geometry.ask.shell.child_radius": "nested core radius",
        "geometry.ask.shell.child_half_length": "nested core half length",
        "geometry.ask.shell.clearance": "shell clearance",
        "geometry.ask.boolean.solid_a_size": "size of boolean solid A (x, y, z)",
        "geometry.ask.boolean.solid_b_size": "size of boolean solid B (x, y, z)",
        "materials.selected_materials": "materials (for example G4_WATER / G4_Al / G4_Si)",
        "materials.volume_material_map": "volume-to-material mapping",
        "source.particle": "particle type (gamma / e- / proton)",
        "source.type": "source type (point / beam / isotropic)",
        "source.energy": "source energy (MeV)",
        "source.position": "source position (x, y, z)",
        "source.direction": "source direction (dx, dy, dz)",
        "physics.physics_list": "physics list (for example FTFP_BERT)",
        "output.format": "output format (root / csv / hdf5 / xml / json)",
        "output.path": "output path",
    },
    "zh": {
        "geometry.structure": "\u51e0\u4f55\u5f62\u72b6\uff08\u4f8b\u5982\u76d2\u4f53\u3001\u5706\u67f1\u3001\u7403\u4f53\u3001\u73af\u5f62\u9635\u5217\u6216\u5806\u53e0\u7ed3\u6784\uff09",
        "geometry.ask.ring.module_size": "\u73af\u5f62\u6a21\u5757\u5c3a\u5bf8\uff08x, y, z\uff09",
        "geometry.ask.ring.count": "\u73af\u5f62\u6a21\u5757\u6570\u91cf",
        "geometry.ask.ring.radius": "\u73af\u5f62\u534a\u5f84",
        "geometry.ask.ring.clearance": "\u73af\u5f62\u95f4\u9699",
        "geometry.ask.grid.module_size": "\u9635\u5217\u6a21\u5757\u5c3a\u5bf8\uff08x, y, z\uff09",
        "geometry.ask.grid.count_x": "x \u65b9\u5411\u9635\u5217\u6570\u91cf",
        "geometry.ask.grid.count_y": "y \u65b9\u5411\u9635\u5217\u6570\u91cf",
        "geometry.ask.grid.pitch_x": "x \u65b9\u5411 pitch",
        "geometry.ask.grid.pitch_y": "y \u65b9\u5411 pitch",
        "geometry.ask.grid.clearance": "\u9635\u5217\u95f4\u9699",
        "geometry.ask.nest.parent_size": "\u5916\u5c42\u76d2\u4f53\u5c3a\u5bf8\uff08x, y, z\uff09",
        "geometry.ask.nest.child_radius": "\u5185\u5d4c\u5706\u67f1\u534a\u5f84",
        "geometry.ask.nest.child_half_length": "\u5185\u5d4c\u5706\u67f1\u534a\u957f",
        "geometry.ask.nest.clearance": "\u5d4c\u5957\u95f4\u9699",
        "geometry.ask.stack.footprint": "\u5806\u53e0\u5c42\u9762\u79ef\u5c3a\u5bf8\uff08x, y\uff09",
        "geometry.ask.stack.thicknesses": "\u5806\u53e0\u5c42\u539a\u5ea6",
        "geometry.ask.stack.layer_clearance": "\u5c42\u95f4\u95f4\u9699",
        "geometry.ask.stack.parent_size": "\u5806\u53e0\u5916\u76d2\u5c3a\u5bf8",
        "geometry.ask.stack.nest_clearance": "\u5806\u53e0\u5916\u76d2\u95f4\u9699",
        "geometry.ask.shell.inner_radius": "\u58f3\u5c42\u5185\u534a\u5f84",
        "geometry.ask.shell.thicknesses": "\u58f3\u5c42\u539a\u5ea6",
        "geometry.ask.shell.half_length": "\u58f3\u5c42\u534a\u957f",
        "geometry.ask.shell.child_radius": "\u5185\u6838\u534a\u5f84",
        "geometry.ask.shell.child_half_length": "\u5185\u6838\u534a\u957f",
        "geometry.ask.shell.clearance": "\u58f3\u5c42\u95f4\u9699",
        "geometry.ask.boolean.solid_a_size": "boolean \u7b2c\u4e00\u4e2a solid \u5c3a\u5bf8\uff08x, y, z\uff09",
        "geometry.ask.boolean.solid_b_size": "boolean \u7b2c\u4e8c\u4e2a solid \u5c3a\u5bf8\uff08x, y, z\uff09",
        "materials.selected_materials": "\u6750\u6599\uff08\u4f8b\u5982 G4_WATER / G4_Al / G4_Si\uff09",
        "materials.volume_material_map": "\u4f53\u79ef\u5230\u6750\u6599\u7684\u6620\u5c04\u5173\u7cfb",
        "source.particle": "\u7c92\u5b50\u7c7b\u578b\uff08gamma / e- / proton\uff09",
        "source.type": "\u6e90\u7c7b\u578b\uff08point / beam / isotropic\uff09",
        "source.energy": "\u6e90\u80fd\u91cf\uff08MeV\uff09",
        "source.position": "\u6e90\u4f4d\u7f6e\uff08x, y, z\uff09",
        "source.direction": "\u6e90\u65b9\u5411\uff08dx, dy, dz\uff09",
        "physics.physics_list": "\u7269\u7406\u5217\u8868\uff08\u4f8b\u5982 FTFP_BERT\uff09",
        "output.format": "\u8f93\u51fa\u683c\u5f0f\uff08root / csv / hdf5 / xml / json\uff09",
        "output.path": "\u8f93\u51fa\u8def\u5f84",
    },
}


def normalize_lang(lang: str) -> str:
    return "zh" if lang == "zh" else "en"


def friendly_label(path: str, lang: str) -> str:
    path = canonical_field_path(path)
    lang_key = normalize_lang(lang)
    if path.startswith("geometry.params."):
        key = path.split(".", 2)[-1]
        return _humanize_param_key(key, lang_key)
    return _FRIENDLY[lang_key].get(path, path)


def friendly_labels(paths: list[str], lang: str) -> list[str]:
    return [friendly_label(path, lang) for path in paths]


_SUMMARY_HIDDEN_PATHS = {
    "geometry.graph_program",
    "geometry.chosen_skeleton",
    "geometry.root_name",
    "materials.selection_source",
    "materials.selection_reasons",
    "source.selection_source",
    "source.selection_reasons",
    "physics.backup_physics_list",
    "physics.covered_processes",
    "physics.selection_source",
    "physics.selection_reasons",
}


def is_user_visible_summary_path(path: str) -> bool:
    path = canonical_field_path(path)
    return bool(path) and path not in _SUMMARY_HIDDEN_PATHS


def clarification_item(path: str, lang: str) -> str:
    path = canonical_field_path(path)
    lang_key = normalize_lang(lang)
    if path.startswith("geometry.params."):
        key = path.split(".", 2)[-1]
        return _humanize_param_key(key, lang_key)
    return _CLARIFICATION[lang_key].get(path, friendly_label(path, lang_key))


def clarification_items(paths: list[str], lang: str) -> list[str]:
    return [clarification_item(path, lang) for path in paths]


def missing_field_question(path: str, lang: str) -> str:
    path = canonical_field_path(path)
    lang_key = normalize_lang(lang)
    if not path:
        return completion_message(lang_key)
    if path in _QUESTION[lang_key]:
        return _QUESTION[lang_key][path]
    return single_field_request(path, lang_key)
