from __future__ import annotations

PARAM_KEYS = [
    "module_x",
    "module_y",
    "module_z",
    "nx",
    "ny",
    "pitch_x",
    "pitch_y",
    "n",
    "radius",
    "clearance",
    "parent_x",
    "parent_y",
    "parent_z",
    "child_rmax",
    "child_hz",
    "rmax1",
    "rmax2",
    "x1",
    "x2",
    "y1",
    "y2",
    "inner_r",
    "th1",
    "th2",
    "th3",
    "hz",
    "stack_x",
    "stack_y",
    "t1",
    "t2",
    "t3",
    "stack_clearance",
    "nest_clearance",
    "tx",
    "ty",
    "tz",
    "rx",
    "ry",
    "rz",
]

ENTITY_KEYS = [
    "material",
    "particle",
    "physics_list",
    "source_type",
    "output_format",
]

STRUCTURE_LABELS = [
    "nest",
    "grid",
    "ring",
    "stack",
    "shell",
    "single_box",
    "single_tubs",
    "single_sphere",
    "single_cons",
    "single_trd",
    "unknown",
]

TOKEN_LABELS = ["O"] + [f"B-{k}" for k in (PARAM_KEYS + ENTITY_KEYS)] + [
    f"I-{k}" for k in (PARAM_KEYS + ENTITY_KEYS)
]
