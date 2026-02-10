from __future__ import annotations

import re
from typing import Dict, List, Tuple


def _parse_value_with_unit(text: str) -> float | None:
    text = text.strip().lower()
    m = re.search(r"([-+]?\d*\.?\d+)", text)
    if not m:
        return None
    value = float(m.group(1))
    if "mm" in text or "毫米" in text:
        value *= 1.0
    elif "cm" in text or "厘米" in text:
        value *= 10.0
    elif "m" in text or "�? in text:
        value *= 1000.0
    return value


def _first_match(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return None
    return _parse_value_with_unit(m.group(1))


def _module_triplet(text: str) -> Tuple[float, float, float] | None:
    m = re.search(
        r"(\d*\.?\d+\s*(?:mm|cm|m|毫米|厘米|�??)\s*(?:x|X|×)\s*"
        r"(\d*\.?\d+\s*(?:mm|cm|m|毫米|厘米|�??)\s*(?:x|X|×)\s*"
        r"(\d*\.?\d+\s*(?:mm|cm|m|毫米|厘米|�??)",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    x = _parse_value_with_unit(m.group(1)) or 0.0
    y = _parse_value_with_unit(m.group(2)) or 0.0
    z = _parse_value_with_unit(m.group(3)) or 0.0
    return x, y, z


def _cube_edge(text: str) -> float | None:
    # Examples: "立方�?边长 1m", "1m立方�?, "cube side 10 cm"
    for pattern in [
        r"(?:edge|side)\s*[:=]?\s*([\d\.]+\s*(?:mm|cm|m)?)",
        r"边长\s*[:=]?\s*([\d\.]+\s*(?:毫米|厘米|�??)",
        r"([\d\.]+\s*(?:mm|cm|m))\s*(?:cube|box)",
        r"([\d\.]+\s*(?:毫米|厘米|�?)\s*立方�?,
    ]:
        val = _first_match(pattern, text)
        if val is not None:
            return val
    return None


def merge_params(text: str, params: Dict[str, float]) -> Tuple[Dict[str, float], List[str]]:
    out = dict(params)
    notes: List[str] = []

    triplet = _module_triplet(text)
    if triplet and not ("module_x" in out and "module_y" in out and "module_z" in out):
        out.setdefault("module_x", triplet[0])
        out.setdefault("module_y", triplet[1])
        out.setdefault("module_z", triplet[2])
        notes.append("filled module_x/module_y/module_z from triplet")
    elif not ("module_x" in out and "module_y" in out and "module_z" in out):
        edge = _cube_edge(text)
        if edge is not None:
            out.setdefault("module_x", edge)
            out.setdefault("module_y", edge)
            out.setdefault("module_z", edge)
            notes.append("filled module_x/module_y/module_z from cube edge")

    for key, pattern in [
        ("radius", r"radius\s*[:=]?\s*([\d\.]+\s*(?:mm|cm)?)"),
        ("radius", r"\bR\s*[:=]?\s*([\d\.]+\s*(?:mm|cm)?)"),
        ("clearance", r"clearance\s*[:=]?\s*([\d\.]+\s*(?:mm|cm)?)"),
        ("clearance", r"gap\s*[:=]?\s*([\d\.]+\s*(?:mm|cm)?)"),
        ("pitch_x", r"pitch[_\s-]*x\s*[:=]?\s*([\d\.]+\s*(?:mm|cm)?)"),
        ("pitch_y", r"pitch[_\s-]*y\s*[:=]?\s*([\d\.]+\s*(?:mm|cm)?)"),
        ("nx", r"\bnx\s*[:=]?\s*(\d+)"),
        ("ny", r"\bny\s*[:=]?\s*(\d+)"),
        ("n", r"\bcount\s*[:=]?\s*(\d+)"),
        ("n", r"\bn\s*[:=]?\s*(\d+)"),
    ]:
        if key in out:
            continue
        val = _first_match(pattern, text)
        if val is None:
            continue
        out[key] = int(round(val)) if key in {"nx", "ny", "n"} else float(val)
        notes.append(f"filled {key} from text")

    # basic cleanup
    for k, v in list(out.items()):
        if k in {"nx", "ny", "n"}:
            out[k] = int(round(v))
        else:
            out[k] = float(v)
        if out[k] < 0:
            out[k] = abs(out[k])
            notes.append(f"clamped {k} to abs")

    return out, notes


