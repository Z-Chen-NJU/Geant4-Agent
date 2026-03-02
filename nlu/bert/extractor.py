from __future__ import annotations

import re

from core.orchestrator.types import CandidateUpdate, Intent, Producer, UpdateOp
from nlu.runtime_semantic import extract_runtime_semantic_frame


def _parse_energy_mev(text: str) -> float | None:
    m = re.search(r"([-+]?\d*\.?\d+)\s*(mev|gev|kev)", text.lower())
    if not m:
        return None
    v = float(m.group(1))
    unit = m.group(2)
    if unit == "gev":
        return v * 1000.0
    if unit == "kev":
        return v * 0.001
    return v


def _value_to_mm(value: float, unit: str) -> float:
    u = unit.strip().lower()
    if u == "m":
        return value * 1000.0
    if u == "cm":
        return value * 10.0
    return value


def _parse_module_triplet_mm(text: str) -> tuple[float, float, float] | None:
    num = r"[-+]?\d*\.?\d+"
    unit = r"(mm|cm|m)"
    pat1 = (
        rf"({num})\s*{unit}\s*[xX*]\s*"
        rf"({num})\s*{unit}\s*[xX*]\s*"
        rf"({num})\s*{unit}"
    )
    m = re.search(pat1, text)
    if m:
        x = _value_to_mm(float(m.group(1)), m.group(2))
        y = _value_to_mm(float(m.group(3)), m.group(4))
        z = _value_to_mm(float(m.group(5)), m.group(6))
        return x, y, z

    pat2 = rf"({num})\s*[xX*]\s*({num})\s*[xX*]\s*({num})\s*{unit}"
    m2 = re.search(pat2, text)
    if not m2:
        return None
    u = m2.group(4)
    return (
        _value_to_mm(float(m2.group(1)), u),
        _value_to_mm(float(m2.group(2)), u),
        _value_to_mm(float(m2.group(3)), u),
    )


def _infer_structure_from_text(text: str) -> str | None:
    low = text.lower()
    if any(k in low for k in ["box", "cube", "立方体", "长方体"]):
        return "single_box"
    if any(k in low for k in ["cylinder", "tubs", "圆柱"]):
        return "single_tubs"
    if any(k in low for k in ["sphere", "球"]):
        return "single_sphere"
    return None


def _infer_particle(text: str) -> str | None:
    low = text.lower()
    if "gamma" in low or "光子" in low:
        return "gamma"
    if "electron" in low or "电子" in low or "e-" in low:
        return "e-"
    if "proton" in low or "质子" in low:
        return "proton"
    if "neutron" in low or "中子" in low:
        return "neutron"
    return None


def _infer_material(text: str) -> str | None:
    low = text.lower()
    if "g4_cu" in low or "copper" in low or "铜" in low:
        return "G4_Cu"
    if "g4_si" in low or "silicon" in low or "硅" in low:
        return "G4_Si"
    if "g4_al" in low or "aluminum" in low or "铝" in low:
        return "G4_Al"
    if "g4_water" in low or "water" in low or "水" in low:
        return "G4_WATER"
    return None


def _infer_output_format(text: str) -> str | None:
    low = text.lower()
    if "root" in low:
        return "root"
    if "json" in low:
        return "json"
    if "csv" in low:
        return "csv"
    return None


def _infer_source_type(text: str) -> str | None:
    low = text.lower()
    if any(k in low for k in ["point source", "point", "点源", "点状源", "点束"]):
        return "point"
    if any(k in low for k in ["beam", "束流", "粒子束"]):
        return "beam"
    if any(k in low for k in ["isotropic", "各向同性"]):
        return "isotropic"
    if any(k in low for k in ["plane source", "plane", "面源"]):
        return "plane"
    return None


def _parse_vector(text: str, key: str) -> dict | None:
    num = r"[-+]?\d*\.?\d+"
    unit = r"(?:\s*(?:mm|cm|m))?"
    sep = r"\s*[,，; ]+\s*"
    pat = (
        rf"{key}\s*[:=]?\s*\(?\s*({num}){unit}{sep}"
        rf"({num}){unit}{sep}"
        rf"({num}){unit}\s*\)?"
    )
    m = re.search(pat, text.lower())
    if not m:
        return None
    return {"type": "vector", "value": [float(m.group(1)), float(m.group(2)), float(m.group(3))]}


def _parse_direction_shorthand(text: str) -> dict | None:
    low = text.lower().replace(" ", "")
    if "+z" in low:
        return {"type": "vector", "value": [0.0, 0.0, 1.0]}
    if "-z" in low:
        return {"type": "vector", "value": [0.0, 0.0, -1.0]}
    if "+x" in low:
        return {"type": "vector", "value": [1.0, 0.0, 0.0]}
    if "-x" in low:
        return {"type": "vector", "value": [-1.0, 0.0, 0.0]}
    if "+y" in low:
        return {"type": "vector", "value": [0.0, 1.0, 0.0]}
    if "-y" in low:
        return {"type": "vector", "value": [0.0, -1.0, 0.0]}
    return None


def _parse_position_shorthand(text: str) -> dict | None:
    low = text.lower()
    if any(k in low for k in ["origin", "center", "原点", "中心"]):
        return {"type": "vector", "value": [0.0, 0.0, 0.0]}
    return None


def _parse_at_to(text: str) -> tuple[dict | None, dict | None]:
    num = r"[-+]?\d*\.?\d+"
    pat = (
        rf"\bat\s*\(?\s*({num})\s*[,，; ]\s*({num})\s*[,，; ]\s*({num})\s*\)?\s*"
        rf"(?:to|towards|->|朝|沿)\s*"
        rf"\(?\s*({num})\s*[,，; ]\s*({num})\s*[,，; ]\s*({num})\s*\)?"
    )
    m = re.search(pat, text.lower())
    if not m:
        return None, None
    pos = {"type": "vector", "value": [float(m.group(1)), float(m.group(2)), float(m.group(3))]}
    direction = {"type": "vector", "value": [float(m.group(4)), float(m.group(5)), float(m.group(6))]}
    return pos, direction


def extract_candidates_from_normalized_text(
    normalized_text: str,
    *,
    raw_text: str = "",
    turn_id: int,
    min_confidence: float,
    context_summary: str,
    config_path: str,
) -> tuple[CandidateUpdate, dict]:
    _ = config_path
    frame, debug = extract_runtime_semantic_frame(
        normalized_text,
        min_confidence=min_confidence,
        device="auto",
        context_summary=context_summary,
    )
    updates: list[UpdateOp] = []
    score = float(debug.get("scores", {}).get("best_prob", 0.6))
    merged_text = f"{raw_text} ; {normalized_text}".strip(" ;")

    if frame.geometry.structure:
        updates.append(
            UpdateOp(
                path="geometry.structure",
                op="set",
                value=frame.geometry.structure,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    for key, value in frame.geometry.params.items():
        updates.append(
            UpdateOp(
                path=f"geometry.params.{key}",
                op="set",
                value=value,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )

    # fallback geometry extraction from raw+normalized text
    if not frame.geometry.structure:
        inferred_structure = _infer_structure_from_text(merged_text)
        if inferred_structure:
            updates.append(
                UpdateOp(
                    path="geometry.structure",
                    op="set",
                    value=inferred_structure,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                )
            )
    triplet = _parse_module_triplet_mm(merged_text)
    if triplet is not None:
        updates.extend(
            [
                UpdateOp(
                    path="geometry.params.module_x",
                    op="set",
                    value=float(triplet[0]),
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                ),
                UpdateOp(
                    path="geometry.params.module_y",
                    op="set",
                    value=float(triplet[1]),
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                ),
                UpdateOp(
                    path="geometry.params.module_z",
                    op="set",
                    value=float(triplet[2]),
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                ),
            ]
        )

    if frame.materials.selected_materials:
        updates.append(
            UpdateOp(
                path="materials.selected_materials",
                op="set",
                value=list(frame.materials.selected_materials),
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    else:
        m = _infer_material(merged_text)
        if m:
            updates.append(
                UpdateOp(
                    path="materials.selected_materials",
                    op="set",
                    value=[m],
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                )
            )

    if frame.source.particle:
        updates.append(
            UpdateOp(
                path="source.particle",
                op="set",
                value=frame.source.particle,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    else:
        particle = _infer_particle(merged_text)
        if particle:
            updates.append(
                UpdateOp(
                    path="source.particle",
                    op="set",
                    value=particle,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                )
            )
    if frame.source.type:
        updates.append(
            UpdateOp(
                path="source.type",
                op="set",
                value=frame.source.type,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    else:
        src_type = _infer_source_type(merged_text)
        if src_type:
            updates.append(
                UpdateOp(
                    path="source.type",
                    op="set",
                    value=src_type,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                )
            )

    if frame.physics.physics_list:
        updates.append(
            UpdateOp(
                path="physics.physics_list",
                op="set",
                value=frame.physics.physics_list,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    if frame.output.format:
        updates.append(
            UpdateOp(
                path="output.format",
                op="set",
                value=frame.output.format,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    else:
        fmt = _infer_output_format(merged_text)
        if fmt:
            updates.append(
                UpdateOp(
                    path="output.format",
                    op="set",
                    value=fmt,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=score,
                    turn_id=turn_id,
                )
            )

    # lightweight kinematics fallbacks from normalized text
    energy = _parse_energy_mev(merged_text)
    if energy is not None:
        updates.append(
            UpdateOp(
                path="source.energy",
                op="set",
                value=energy,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    pos = _parse_vector(merged_text, "position") or _parse_position_shorthand(merged_text)
    at_pos, at_dir = _parse_at_to(merged_text)
    if pos is None and at_pos is not None:
        pos = at_pos
    if pos is not None:
        updates.append(
            UpdateOp(
                path="source.position",
                op="set",
                value=pos,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )
    direction = _parse_vector(merged_text, "direction") or _parse_direction_shorthand(merged_text)
    if direction is None and at_dir is not None:
        direction = at_dir
    if direction is not None:
        updates.append(
            UpdateOp(
                path="source.direction",
                op="set",
                value=direction,
                producer=Producer.BERT_EXTRACTOR,
                confidence=score,
                turn_id=turn_id,
            )
        )

    deduped_updates: dict[str, UpdateOp] = {}
    for update in updates:
        deduped_updates[update.path] = update
    updates = list(deduped_updates.values())

    candidate = CandidateUpdate(
        producer=Producer.BERT_EXTRACTOR,
        intent=Intent.SET,
        target_paths=[u.path for u in updates],
        updates=updates,
        confidence=score,
        rationale=debug.get("inference_backend", "bert_extractor"),
    )
    return candidate, debug
