from __future__ import annotations

import re

_UNCERTAINTY_PATTERNS = (
    r"\b(?:have\s+not\s+fixed|haven't\s+fixed|not\s+fixed(?:\s+yet)?|not\s+decided|undecided|unresolved|unspecified|not\s+sure|unknown|pending|tbd|to\s+be\s+decided)\b",
    r"(?:缺参|参数不全|先给一个缺参开头|先缺参|未定|尚未确定|不确定|还没定|未指定|暂未确定)",
)

_GENERAL_MISSING_PATTERNS = (
    r"\b(?:missing\s+parameters?|incomplete\s+start)\b",
    r"(?:缺参|参数不全|先给一个缺参开头|先缺参)",
)

_DEFAULT_UNRESOLVED_TARGETS = {
    "geometry.kind",
    "materials.primary",
    "source.kind",
    "source.particle",
    "source.energy_mev",
    "source.position_mm",
    "source.direction_vec",
    "physics.explicit_list",
    "output.format",
}

_TARGET_KEYWORDS = {
    "geometry.kind": ("geometry", "shape", "target shape", "structure", "layout", "几何", "形状", "构型", "结构", "布局"),
    "materials.primary": ("material", "materials", "材质", "材料"),
    "source.kind": ("source type", "source", "beam type", "源类型", "源"),
    "source.particle": ("particle", "particles", "photon", "gamma", "neutron", "electron", "proton", "粒子", "光子", "伽马", "中子", "电子", "质子"),
    "source.energy_mev": ("source energy", "beam energy", "energy", "能量"),
    "source.position_mm": ("source position", "position", "location", "位置", "坐标"),
    "source.direction_vec": ("direction", "forward", "pointing", "朝向", "方向"),
    "physics.explicit_list": ("physics list", "physics", "物理列表", "物理过程"),
    "output.format": ("output format", "format", "输出格式", "输出"),
}

_TARGET_GROUNDED_PATTERNS = {
    "geometry.kind": (
        r"\b(?:box|cube|cuboid|cylinder|cylindrical|tubs|sphere|orb|cons|cone|frustum|trd|trap|para|torus|ellipsoid|elltube|polycone|polyhedra|cuttubs|ring|grid|nest|stack|shell|boolean|union|subtraction|intersection)\b",
        r"(?:立方体|长方体|圆柱|球|圆锥|截锥|环|阵列|嵌套|堆叠|壳层|布尔)",
        r"\b[-+]?\d*\.?\d+\s*(?:mm|cm|m)\s*(?:x|by)\s*[-+]?\d*\.?\d+\s*(?:mm|cm|m)\s*(?:x|by)\s*[-+]?\d*\.?\d+\s*(?:mm|cm|m)\b",
        r"\b(?:radius|diameter|half[-\s]*length|height|length)\s*[:=]?\s*[-+]?\d*\.?\d+\s*(?:mm|cm|m)\b",
        r"(?:半径|直径|半长|高度|长度)\s*[:=]?\s*[-+]?\d*\.?\d+\s*(?:毫米|厘米|米|mm|cm|m)",
    ),
    "materials.primary": (
        r"\b(?:g4_[a-z0-9_-]+|air|water|silicon|copper|aluminum|aluminium|iron|steel|stainless steel|lead|tungsten)\b",
        r"(?:空气|水|硅|铜|铝|铁|钢|铅|钨)",
    ),
    "source.kind": (
        r"\b(?:point source|point|beam|plane|isotropic)\b",
        r"(?:点源|束流|平面源|各向同性)",
    ),
    "source.particle": (
        r"\b(?:gamma|photon|photons|electron|electrons|proton|protons|neutron|neutrons|e-)\b",
        r"(?:伽马|光子|电子|质子|中子)",
    ),
    "source.energy_mev": (r"\b[-+]?\d*\.?\d+\s*(?:mev|gev|kev)\b", r"[-+]?\d*\.?\d+\s*(?:兆电子伏|千电子伏|吉电子伏)"),
    "source.position_mm": (
        r"\(\s*[-+0-9.]+\s*,\s*[-+0-9.]+\s*,\s*[-+0-9.]+\s*\)",
        r"(?:origin|center|centre|位置|原点|中心)",
    ),
    "source.direction_vec": (
        r"(?:\+|-)[xyz]\b",
        r"\(\s*[-+0-9.]+\s*,\s*[-+0-9.]+\s*,\s*[-+0-9.]+\s*\)",
        r"(?:along|toward|towards|pointing|direction|方向|沿着|朝向)",
    ),
    "physics.explicit_list": (r"\b(?:ftfp(?:_bert(?:_hp)?)?|qgsp(?:_bert(?:_hp)?)?|qbbc|shielding|emstandard(?:_opt\d+)?)\b",),
    "output.format": (r"\b(?:root|json|csv|xml|hdf5|h5)\b", r"(?:输出\s*格式)"),
}


def has_uncertainty_signal(text: str) -> bool:
    compact = (text or "").strip()
    if not compact:
        return False
    return any(re.search(pattern, compact, flags=re.IGNORECASE) for pattern in _UNCERTAINTY_PATTERNS)


def infer_unresolved_targets(text: str) -> set[str]:
    compact = (text or "").strip()
    if not compact:
        return set()
    low = compact.lower()
    unresolved: set[str] = set()
    if any(re.search(pattern, compact, flags=re.IGNORECASE) for pattern in _GENERAL_MISSING_PATTERNS):
        unresolved.update(_DEFAULT_UNRESOLVED_TARGETS)
    if not has_uncertainty_signal(compact):
        return unresolved
    for target, keywords in _TARGET_KEYWORDS.items():
        if any(keyword.lower() in low for keyword in keywords):
            unresolved.add(target)
    return unresolved


def has_grounded_payload_for_target(text: str, target: str) -> bool:
    compact = (text or "").strip()
    if not compact:
        return False
    patterns = _TARGET_GROUNDED_PATTERNS.get(target, ())
    return any(re.search(pattern, compact, flags=re.IGNORECASE) for pattern in patterns)
