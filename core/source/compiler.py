from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.contracts.semantic import SemanticFrame
from core.contracts.slots import SlotFrame
from core.source.catalog import SourceCatalogEntry, get_source_catalog_entry, resolve_source_type
from core.source.spec import SourceEvidence, SourceFieldResolution, SourceIntent, SourceSpec


@dataclass(frozen=True)
class SourceCompileResult:
    intent: SourceIntent
    spec: SourceSpec | None
    missing_fields: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return self.spec is not None and not self.errors


def _append_field_if_present(
    *,
    fields: dict[str, Any],
    evidence: list[SourceEvidence],
    field_resolutions: dict[str, SourceFieldResolution],
    field_def: SourceCatalogEntry | Any,
    field_name: str,
    value: Any,
    source: str,
    confidence: float,
    detail: str = "",
    status: str = "derived",
) -> None:
    normalized = field_def.normalize_value(value)
    if normalized is None:
        return
    fields[field_name] = normalized
    evidence.append(SourceEvidence(source=source, field=field_name, value=normalized, confidence=confidence, detail=detail))
    field_resolutions[field_name] = SourceFieldResolution(
        field=field_name,
        value=normalized,
        status=status,
        evidence_sources=(source,),
        note=detail,
    )


def _collect_slot_source_fields(entry: SourceCatalogEntry, frame: SlotFrame) -> tuple[dict[str, Any], list[SourceEvidence], dict[str, SourceFieldResolution]]:
    fields: dict[str, Any] = {}
    evidence: list[SourceEvidence] = []
    field_resolutions: dict[str, SourceFieldResolution] = {}
    confidence = float(frame.confidence or 0.8)
    for field_def in entry.fields:
        for slot_field in field_def.slot_fields:
            value = getattr(frame.source, slot_field, None)
            if value is None:
                continue
            _append_field_if_present(
                fields=fields,
                evidence=evidence,
                field_resolutions=field_resolutions,
                field_def=field_def,
                field_name=field_def.name,
                value=value,
                source="slot_frame",
                confidence=confidence,
                detail=slot_field,
                status="user_explicit",
            )
            break
    return fields, evidence, field_resolutions


def build_source_intent_from_slot_frame(frame: SlotFrame) -> SourceIntent:
    source_type = resolve_source_type(frame.source.kind)
    entry = get_source_catalog_entry(source_type)
    fields, evidence, field_resolutions = _collect_slot_source_fields(entry, frame) if entry is not None else ({}, [], {})
    intent = SourceIntent(source_type=source_type, fields=fields, evidence=evidence, field_resolutions=field_resolutions)
    if entry is None:
        if frame.source.kind:
            intent.ambiguities.append(f"unsupported_source_type:{frame.source.kind}")
        return intent
    for required_field in entry.required_fields:
        if required_field not in fields:
            intent.missing_fields.append(required_field)
    return intent


def build_source_intent_from_semantic_frame(frame: SemanticFrame) -> SourceIntent:
    source_type = resolve_source_type(frame.source.type)
    entry = get_source_catalog_entry(source_type)
    fields: dict[str, Any] = {}
    evidence: list[SourceEvidence] = []
    field_resolutions: dict[str, SourceFieldResolution] = {}
    if entry is not None:
        for field_def in entry.fields:
            for key in field_def.semantic_keys:
                value = getattr(frame.source, key, None)
                if value is None:
                    continue
                _append_field_if_present(
                    fields=fields,
                    evidence=evidence,
                    field_resolutions=field_resolutions,
                    field_def=field_def,
                    field_name=field_def.name,
                    value=value,
                    source="semantic_frame",
                    confidence=1.0,
                    detail=key,
                    status="carried_forward",
                )
                break
    intent = SourceIntent(source_type=source_type, fields=fields, evidence=evidence, field_resolutions=field_resolutions)
    if entry is None:
        if frame.source.type:
            intent.ambiguities.append(f"unsupported_source_type:{frame.source.type}")
        return intent
    for required_field in entry.required_fields:
        if required_field not in fields:
            intent.missing_fields.append(required_field)
    return intent


def build_source_intent_from_config(config: dict[str, Any]) -> SourceIntent:
    source = config.get("source", {}) if isinstance(config.get("source"), dict) else {}
    source_type = resolve_source_type(source.get("type"))
    entry = get_source_catalog_entry(source_type)
    fields: dict[str, Any] = {}
    evidence: list[SourceEvidence] = []
    field_resolutions: dict[str, SourceFieldResolution] = {}
    if entry is not None:
        for field_def in entry.fields:
            for key in field_def.config_keys:
                value = source.get(key)
                if value is None:
                    continue
                _append_field_if_present(
                    fields=fields,
                    evidence=evidence,
                    field_resolutions=field_resolutions,
                    field_def=field_def,
                    field_name=field_def.name,
                    value=value,
                    source="config",
                    confidence=1.0,
                    detail=key,
                    status="carried_forward",
                )
                break
    intent = SourceIntent(source_type=source_type, fields=fields, evidence=evidence, field_resolutions=field_resolutions)
    if entry is None:
        if source.get("type"):
            intent.ambiguities.append(f"unsupported_source_type:{source.get('type')}")
        return intent
    for required_field in entry.required_fields:
        if required_field not in fields:
            intent.missing_fields.append(required_field)
    return intent


def compile_source_intent(intent: SourceIntent) -> SourceCompileResult:
    if not intent.source_type:
        return SourceCompileResult(intent=intent, spec=None, errors=("missing_source_type",))
    entry = get_source_catalog_entry(intent.source_type)
    if entry is None:
        return SourceCompileResult(intent=intent, spec=None, errors=(f"unsupported_source_type:{intent.source_type}",))
    missing_fields = list(intent.missing_fields)
    for field_def in entry.fields:
        if field_def.required and field_def.name not in intent.fields and field_def.name not in missing_fields:
            missing_fields.append(field_def.name)
    if missing_fields:
        return SourceCompileResult(intent=intent, spec=None, missing_fields=tuple(missing_fields))
    spec = SourceSpec(
        source_type=entry.source_type,
        fields=dict(intent.fields),
        confidence=max((item.confidence for item in intent.evidence), default=1.0),
        finalization_status="ready" if not intent.ambiguities else "ambiguous",
        field_resolutions=dict(intent.field_resolutions),
    )
    return SourceCompileResult(intent=intent, spec=spec)


def compile_source_spec_from_slot_frame(frame: SlotFrame) -> SourceCompileResult:
    return compile_source_intent(build_source_intent_from_slot_frame(frame))


def compile_source_spec_from_semantic_frame(frame: SemanticFrame) -> SourceCompileResult:
    return compile_source_intent(build_source_intent_from_semantic_frame(frame))


def compile_source_spec_from_config(config: dict[str, Any]) -> SourceCompileResult:
    return compile_source_intent(build_source_intent_from_config(config))
