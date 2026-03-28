from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.interpreter.spec import (
    EvidenceSpan,
    GeometryCandidate,
    SourceCandidate,
    TurnSummary,
)
from nlu.llm_support.ollama_client import extract_json


@dataclass
class InterpreterParseResult:
    ok: bool
    turn_summary: TurnSummary
    geometry_candidate: GeometryCandidate
    source_candidate: SourceCandidate
    raw_payload: dict[str, Any]
    error: str | None = None


def _coerce_evidence_spans(value: Any) -> list[EvidenceSpan]:
    items = value if isinstance(value, list) else []
    spans: list[EvidenceSpan] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        role = str(item.get("role", "")).strip()
        if not text or not role:
            continue
        spans.append(EvidenceSpan(text=text, role=role))
    return spans


def _coerce_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            result.append(text)
    return result


def parse_interpreter_response(raw_text: str) -> InterpreterParseResult:
    payload = extract_json(raw_text or "")
    if not isinstance(payload, dict):
        return InterpreterParseResult(
            ok=False,
            turn_summary=TurnSummary(),
            geometry_candidate=GeometryCandidate(),
            source_candidate=SourceCandidate(),
            raw_payload={},
            error="json_parse_failed",
        )

    turn_payload = payload.get("turn_summary")
    turn_dict = turn_payload if isinstance(turn_payload, dict) else {}
    geometry_payload = payload.get("geometry_candidate")
    geometry_dict = geometry_payload if isinstance(geometry_payload, dict) else {}
    source_payload = payload.get("source_candidate")
    source_dict = source_payload if isinstance(source_payload, dict) else {}

    summary = TurnSummary(
        intent=str(turn_dict.get("intent", "other")).strip().lower() or "other",
        focus=str(turn_dict.get("focus", "mixed")).strip().lower() or "mixed",
        scope=str(turn_dict.get("scope", "partial_update")).strip().lower() or "partial_update",
        user_goal=str(turn_dict.get("user_goal", "")).strip(),
        explicit_domains=_coerce_str_list(turn_dict.get("explicit_domains")),
        uncertain_domains=_coerce_str_list(turn_dict.get("uncertain_domains")),
    )

    geometry_candidate = GeometryCandidate(
        kind_candidate=str(geometry_dict.get("kind_candidate")).strip() if geometry_dict.get("kind_candidate") is not None else None,
        material_candidate=str(geometry_dict.get("material_candidate")).strip() if geometry_dict.get("material_candidate") is not None else None,
        dimension_hints=dict(geometry_dict.get("dimension_hints", {})) if isinstance(geometry_dict.get("dimension_hints"), dict) else {},
        placement_relation=str(geometry_dict.get("placement_relation")).strip() if geometry_dict.get("placement_relation") is not None else None,
        confidence=float(geometry_dict.get("confidence", 0.0) or 0.0),
        ambiguities=_coerce_str_list(geometry_dict.get("ambiguities")),
        evidence_spans=_coerce_evidence_spans(geometry_dict.get("evidence_spans")),
    )

    source_candidate = SourceCandidate(
        source_type_candidate=str(source_dict.get("source_type_candidate")).strip() if source_dict.get("source_type_candidate") is not None else None,
        particle_candidate=str(source_dict.get("particle_candidate")).strip() if source_dict.get("particle_candidate") is not None else None,
        energy_candidate_mev=float(source_dict.get("energy_candidate_mev")) if source_dict.get("energy_candidate_mev") is not None else None,
        position_mode=str(source_dict.get("position_mode")).strip() if source_dict.get("position_mode") is not None else None,
        position_hint=dict(source_dict.get("position_hint", {})) if isinstance(source_dict.get("position_hint"), dict) else {},
        direction_mode=str(source_dict.get("direction_mode")).strip() if source_dict.get("direction_mode") is not None else None,
        direction_hint=dict(source_dict.get("direction_hint", {})) if isinstance(source_dict.get("direction_hint"), dict) else {},
        confidence=float(source_dict.get("confidence", 0.0) or 0.0),
        ambiguities=_coerce_str_list(source_dict.get("ambiguities")),
        evidence_spans=_coerce_evidence_spans(source_dict.get("evidence_spans")),
    )

    return InterpreterParseResult(
        ok=True,
        turn_summary=summary,
        geometry_candidate=geometry_candidate,
        source_candidate=source_candidate,
        raw_payload=payload,
        error=None,
    )
