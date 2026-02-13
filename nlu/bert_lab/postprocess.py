from __future__ import annotations

import re
from typing import Dict, List, Tuple

MM_WORDS = ("mm", "\u6beb\u7c73")
CM_WORDS = ("cm", "\u5398\u7c73")
M_WORDS = ("\u7c73",)


def _parse_value_with_unit(text: str) -> float | None:
    text_l = text.strip().lower()
    m = re.search(r"([-+]?\d*\.?\d+)", text_l)
    if not m:
        return None
    value = float(m.group(1))

    if any(w in text_l for w in MM_WORDS):
        return value
    if any(w in text_l for w in CM_WORDS):
        return value * 10.0
    if any(w in text_l for w in M_WORDS):
        return value * 1000.0
    if re.search(r"\d(?:\.\d+)?\s*m\b", text_l) and ("mm" not in text_l and "cm" not in text_l):
        return value * 1000.0
    return value


def _first_match(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return None
    return _parse_value_with_unit(m.group(1))


def _module_triplet(text: str) -> Tuple[float, float, float] | None:
    unit = r"(?:mm|cm|m|\u6beb\u7c73|\u5398\u7c73|\u7c73)"
    m = re.search(
        rf"(\d*\.?\d+\s*{unit})\s*(?:x|X|\*)\s*"
        rf"(\d*\.?\d+\s*{unit})\s*(?:x|X|\*)\s*"
        rf"(\d*\.?\d+\s*{unit})",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return None

    x = _parse_value_with_unit(m.group(1))
    y = _parse_value_with_unit(m.group(2))
    z = _parse_value_with_unit(m.group(3))
    if x is None or y is None or z is None:
        m2 = re.search(
            rf"(\d*\.?\d+)\s*(?:x|X|\*)\s*(\d*\.?\d+)\s*(?:x|X|\*)\s*(\d*\.?\d+)\s*({unit})",
            text,
            flags=re.IGNORECASE,
        )
        if not m2:
            return None
        suffix = m2.group(4)
        x = _parse_value_with_unit(f"{m2.group(1)} {suffix}")
        y = _parse_value_with_unit(f"{m2.group(2)} {suffix}")
        z = _parse_value_with_unit(f"{m2.group(3)} {suffix}")
        if x is None or y is None or z is None:
            return None
    return x, y, z


def _all_triplets(text: str) -> List[Tuple[float, float, float]]:
    unit = r"(?:mm|cm|m|\u6beb\u7c73|\u5398\u7c73|\u7c73)"
    pattern = re.compile(
        rf"(\d*\.?\d+\s*{unit})\s*(?:x|X|\*)\s*"
        rf"(\d*\.?\d+\s*{unit})\s*(?:x|X|\*)\s*"
        rf"(\d*\.?\d+\s*{unit})",
        flags=re.IGNORECASE,
    )
    out: List[Tuple[float, float, float]] = []
    for m in pattern.finditer(text):
        x = _parse_value_with_unit(m.group(1))
        y = _parse_value_with_unit(m.group(2))
        z = _parse_value_with_unit(m.group(3))
        if x is None or y is None or z is None:
            continue
        out.append((x, y, z))
    compact = re.compile(
        rf"(\d*\.?\d+)\s*(?:x|X|\*)\s*(\d*\.?\d+)\s*(?:x|X|\*)\s*(\d*\.?\d+)\s*({unit})",
        flags=re.IGNORECASE,
    )
    for m in compact.finditer(text):
        suffix = m.group(4)
        x = _parse_value_with_unit(f"{m.group(1)} {suffix}")
        y = _parse_value_with_unit(f"{m.group(2)} {suffix}")
        z = _parse_value_with_unit(f"{m.group(3)} {suffix}")
        if x is None or y is None or z is None:
            continue
        out.append((x, y, z))
    return out


def _cube_edge(text: str) -> float | None:
    unit = r"(?:mm|cm|m|\u6beb\u7c73|\u5398\u7c73|\u7c73)"
    patterns = [
        rf"(?:edge|side)\s*[:=]?\s*([\d\.]+\s*{unit})",
        rf"\u8fb9\u957f\s*[:=]?\s*([\d\.]+\s*{unit})",
        rf"([\d\.]+\s*{unit})\s*(?:cube|box)",
        rf"([\d\.]+\s*{unit})\s*\u7acb\u65b9\u4f53",
    ]
    for pattern in patterns:
        val = _first_match(pattern, text)
        if val is not None:
            return val
    return None


def _fill_by_patterns(text: str, out: Dict[str, float], notes: List[str]) -> None:
    unit = r"(?:mm|cm|m|\u6beb\u7c73|\u5398\u7c73|\u7c73)?"
    num = r"[+\-]?\d*\.?\d+"
    for key, pattern in [
        ("module_x", rf"(?:module[_\s-]*x)\s*[:=]?\s*({num}\s*{unit})"),
        ("module_y", rf"(?:module[_\s-]*y)\s*[:=]?\s*({num}\s*{unit})"),
        ("module_z", rf"(?:module[_\s-]*z)\s*[:=]?\s*({num}\s*{unit})"),
        ("parent_x", rf"(?:parent[_\s-]*x)\s*[:=]?\s*({num}\s*{unit})"),
        ("parent_y", rf"(?:parent[_\s-]*y)\s*[:=]?\s*({num}\s*{unit})"),
        ("parent_z", rf"(?:parent[_\s-]*z)\s*[:=]?\s*({num}\s*{unit})"),
        ("child_rmax", rf"(?:child[_\s-]*rmax|rmax)\s*[:=]?\s*({num}\s*{unit})"),
        ("child_hz", rf"(?:child[_\s-]*hz|hz)\s*[:=]?\s*({num}\s*{unit})"),
        ("rmax1", rf"\brmax1\b\s*[:=]?\s*({num}\s*{unit})"),
        ("rmax2", rf"\brmax2\b\s*[:=]?\s*({num}\s*{unit})"),
        ("x1", rf"\bx1\b\s*[:=]?\s*({num}\s*{unit})"),
        ("x2", rf"\bx2\b\s*[:=]?\s*({num}\s*{unit})"),
        ("y1", rf"\by1\b\s*[:=]?\s*({num}\s*{unit})"),
        ("y2", rf"\by2\b\s*[:=]?\s*({num}\s*{unit})"),
        ("z1", rf"\bz1\b\s*[:=]?\s*({num}\s*{unit})"),
        ("z2", rf"\bz2\b\s*[:=]?\s*({num}\s*{unit})"),
        ("z3", rf"\bz3\b\s*[:=]?\s*({num}\s*{unit})"),
        ("r1", rf"\br1\b\s*[:=]?\s*({num}\s*{unit})"),
        ("r2", rf"\br2\b\s*[:=]?\s*({num}\s*{unit})"),
        ("r3", rf"\br3\b\s*[:=]?\s*({num}\s*{unit})"),
        ("tilt_x", rf"(?:tilt[_\s-]*x)\s*[:=]?\s*({num})"),
        ("tilt_y", rf"(?:tilt[_\s-]*y)\s*[:=]?\s*({num})"),
        ("bool_a_x", rf"(?:bool[_\s-]*a[_\s-]*x)\s*[:=]?\s*({num}\s*{unit})"),
        ("bool_a_y", rf"(?:bool[_\s-]*a[_\s-]*y)\s*[:=]?\s*({num}\s*{unit})"),
        ("bool_a_z", rf"(?:bool[_\s-]*a[_\s-]*z)\s*[:=]?\s*({num}\s*{unit})"),
        ("bool_b_x", rf"(?:bool[_\s-]*b[_\s-]*x)\s*[:=]?\s*({num}\s*{unit})"),
        ("bool_b_y", rf"(?:bool[_\s-]*b[_\s-]*y)\s*[:=]?\s*({num}\s*{unit})"),
        ("bool_b_z", rf"(?:bool[_\s-]*b[_\s-]*z)\s*[:=]?\s*({num}\s*{unit})"),
        ("stack_x", rf"(?:stack[_\s-]*x)\s*[:=]?\s*({num}\s*{unit})"),
        ("stack_y", rf"(?:stack[_\s-]*y)\s*[:=]?\s*({num}\s*{unit})"),
        ("t1", rf"\bt1\b\s*[:=]?\s*({num}\s*{unit})"),
        ("t2", rf"\bt2\b\s*[:=]?\s*({num}\s*{unit})"),
        ("t3", rf"\bt3\b\s*[:=]?\s*({num}\s*{unit})"),
        ("stack_clearance", rf"(?:stack[_\s-]*clearance)\s*[:=]?\s*({num}\s*{unit})"),
        ("nest_clearance", rf"(?:nest[_\s-]*clearance)\s*[:=]?\s*({num}\s*{unit})"),
        ("inner_r", rf"(?:inner[_\s-]*r)\s*[:=]?\s*({num}\s*{unit})"),
        ("th1", rf"\bth1\b\s*[:=]?\s*({num}\s*{unit})"),
        ("th2", rf"\bth2\b\s*[:=]?\s*({num}\s*{unit})"),
        ("th3", rf"\bth3\b\s*[:=]?\s*({num}\s*{unit})"),
        ("tx", rf"\btx\b\s*[:=]?\s*({num}\s*{unit})"),
        ("ty", rf"\bty\b\s*[:=]?\s*({num}\s*{unit})"),
        ("tz", rf"\btz\b\s*[:=]?\s*({num}\s*{unit})"),
        ("rx", rf"\brx\b\s*[:=]?\s*({num})"),
        ("ry", rf"\bry\b\s*[:=]?\s*({num})"),
        ("rz", rf"\brz\b\s*[:=]?\s*({num})"),
    ]:
        if key in out:
            continue
        val = _first_match(pattern, text)
        if val is None:
            continue
        out[key] = float(val)
        notes.append(f"filled {key} from key/value")

    if "n" not in out:
        m = re.search(r"\b(\d+)\s+modules?\b", text, flags=re.IGNORECASE)
        if m:
            out["n"] = int(m.group(1))
            notes.append("filled n from modules count")


def merge_params(text: str, params: Dict[str, float]) -> Tuple[Dict[str, float], List[str]]:
    out = dict(params)
    notes: List[str] = []
    _fill_by_patterns(text, out, notes)

    boolean_context = "boolean" in text.lower()
    if not boolean_context:
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

    if boolean_context or ("bool_a_x" in out or "bool_b_x" in out):
        trips = _all_triplets(text)
        if len(trips) >= 2:
            a = trips[0]
            b = trips[1]
            if "bool_a_x" not in out:
                out["bool_a_x"] = a[0]
                out["bool_a_y"] = a[1]
                out["bool_a_z"] = a[2]
                notes.append("filled bool_a_* from first triplet")
            if "bool_b_x" not in out:
                out["bool_b_x"] = b[0]
                out["bool_b_y"] = b[1]
                out["bool_b_z"] = b[2]
                notes.append("filled bool_b_* from second triplet")

    for key, pattern in [
        ("radius", r"\bradius\b\s*[:=]?\s*([\d\.]+\s*(?:mm|cm|m)?)"),
        ("radius", r"\bR(?!\d)\b\s*[:=]?\s*([\d\.]+\s*(?:mm|cm|m)?)"),
        ("clearance", r"clearance\s*[:=]?\s*([\d\.]+\s*(?:mm|cm|m)?)"),
        ("clearance", r"gap\s*[:=]?\s*([\d\.]+\s*(?:mm|cm|m)?)"),
        ("pitch_x", r"pitch[_\s-]*x\s*[:=]?\s*([\d\.]+\s*(?:mm|cm|m)?)"),
        ("pitch_y", r"pitch[_\s-]*y\s*[:=]?\s*([\d\.]+\s*(?:mm|cm|m)?)"),
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

    for k, v in list(out.items()):
        if k in {"nx", "ny", "n"}:
            out[k] = int(round(v))
        else:
            out[k] = float(v)

    return out, notes
