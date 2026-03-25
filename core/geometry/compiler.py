from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.contracts.slots import SlotFrame

from core.geometry.catalog import get_geometry_catalog_entry, resolve_geometry_structure
from core.geometry.spec import GeometryEvidence, GeometryIntent, GeometrySpec


@dataclass(frozen=True)
class GeometryCompileResult:
    intent: GeometryIntent
    spec: GeometrySpec | None
    missing_fields: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return self.spec is not None and not self.errors


def _float_triplet(values: Any) -> list[float] | None:
    if not isinstance(values, (list, tuple)) or len(values) != 3:
        return None
    return [float(values[0]), float(values[1]), float(values[2])]


def _collect_intent_params(structure: str, frame: SlotFrame) -> tuple[dict[str, Any], list[GeometryEvidence]]:
    params: dict[str, Any] = {}
    evidence: list[GeometryEvidence] = []

    def add(field: str, value: Any) -> None:
        params[field] = value
        evidence.append(
            GeometryEvidence(
                source="slot_frame",
                field=field,
                value=value,
                confidence=float(frame.confidence or 0.8),
            )
        )

    if structure == "single_box":
        triplet = _float_triplet(frame.geometry.size_triplet_mm)
        if triplet:
            add("size_triplet_mm", triplet)
    elif structure == "single_tubs":
        if frame.geometry.radius_mm is not None:
            add("radius_mm", float(frame.geometry.radius_mm))
        if frame.geometry.half_length_mm is not None:
            add("half_length_mm", float(frame.geometry.half_length_mm))

    return params, evidence


def build_geometry_intent_from_slot_frame(frame: SlotFrame) -> GeometryIntent:
    structure = resolve_geometry_structure(frame.geometry.kind)
    params, evidence = _collect_intent_params(structure or "", frame)
    intent = GeometryIntent(
        structure=structure,
        kind=frame.geometry.kind,
        params=params,
        evidence=evidence,
    )
    entry = get_geometry_catalog_entry(structure)
    if entry is None:
        if frame.geometry.kind:
            intent.ambiguities.append(f"unsupported_geometry_kind:{frame.geometry.kind}")
        return intent
    for required_field in entry.required_slot_fields:
        if required_field == "kind":
            if not frame.geometry.kind:
                intent.missing_fields.append(required_field)
        elif required_field not in params:
            intent.missing_fields.append(required_field)
    return intent


def compile_geometry_intent(intent: GeometryIntent) -> GeometryCompileResult:
    if not intent.structure:
        return GeometryCompileResult(
            intent=intent,
            spec=None,
            errors=("missing_geometry_structure",),
        )
    entry = get_geometry_catalog_entry(intent.structure)
    if entry is None:
        return GeometryCompileResult(
            intent=intent,
            spec=None,
            errors=(f"unsupported_geometry_structure:{intent.structure}",),
        )

    missing_fields = list(intent.missing_fields)
    for param in entry.params:
        if param.required and param.name not in intent.params and param.name not in missing_fields:
            missing_fields.append(param.name)
    if missing_fields:
        return GeometryCompileResult(
            intent=intent,
            spec=None,
            missing_fields=tuple(missing_fields),
        )

    spec = GeometrySpec(
        structure=entry.structure,
        params=dict(intent.params),
        allowed_paths=entry.allowed_paths,
        required_paths=entry.required_paths,
    )
    return GeometryCompileResult(intent=intent, spec=spec)


def compile_geometry_spec_from_slot_frame(frame: SlotFrame) -> GeometryCompileResult:
    intent = build_geometry_intent_from_slot_frame(frame)
    return compile_geometry_intent(intent)

