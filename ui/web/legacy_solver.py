from __future__ import annotations

from typing import Any, Dict

from builder.geometry.synthesize import synthesize_from_params
from nlu.llm_support.llm_bridge import build_missing_params_prompt, build_missing_params_schema
from nlu.llm_support.ollama_client import chat, extract_json
from ui.web.runtime_state import get_ollama_config_path


def solve_payload(
    *,
    text: str,
    top_k: int,
    min_confidence: float,
    normalize_input: bool,
    prompt_format: str,
    autofix: bool,
    llm_fill_missing: bool,
    params_override: dict[str, Any],
    extract_semantic_frame,
) -> Dict[str, Any]:
    frame, debug = extract_semantic_frame(
        text,
        min_confidence=min_confidence,
        device="auto",
        normalize_with_llm=normalize_input,
        normalize_config_path=get_ollama_config_path(),
        context_summary="",
    )
    if bool(debug.get("requires_llm_normalization", False)):
        return {
            "structure": "unknown",
            "inference_backend": debug.get("inference_backend", "deferred_non_english"),
            "normalized_text": debug.get("normalized_text", text),
            "normalization": debug.get("normalization", {}),
            "normalization_degraded": bool(debug.get("normalization_degraded", False)),
            "requires_llm_normalization": True,
            "scores": {},
            "params": {},
            "notes": list(frame.notes),
            "synthesis": {"error": "requires_llm_normalization"},
            "missing_prompt": "",
            "missing_schema": None,
            "candidates": [],
            "best_candidate": None,
        }

    structure = frame.geometry.structure or "unknown"
    params = dict(frame.geometry.params)
    params.update(params_override)
    notes = list(frame.notes)
    scores = debug.get("scores", {})
    ranked = debug.get("ranked", [])

    candidates = []
    for name, prob in ranked[: max(1, top_k)]:
        if prob < min_confidence:
            continue
        synth = synthesize_from_params(name, params, seed=7, apply_autofix=autofix)
        missing = synth.get("missing_params", [])
        prompt = build_missing_params_prompt(name, missing, fmt=prompt_format)
        schema = build_missing_params_schema(name, missing) if prompt_format == "json_schema" else None
        filled = None
        if llm_fill_missing and missing:
            resp = chat(prompt, config_path=get_ollama_config_path(), temperature=0.2)
            parsed = extract_json(resp.get("response", ""))
            if isinstance(parsed, dict):
                merged = dict(params)
                merged.update(parsed)
                filled = synthesize_from_params(name, merged, seed=7, apply_autofix=autofix)
        candidates.append(
            {
                "structure": name,
                "prob": prob,
                "synthesis": synth,
                "synthesis_filled": filled,
                "missing_prompt": prompt,
                "missing_schema": schema,
            }
        )

    if structure == "unknown":
        synthesis = {"error": "structure confidence below threshold"}
        missing_prompt = ""
        missing_schema = None
    else:
        synthesis = synthesize_from_params(structure, params, seed=7, apply_autofix=autofix)
        missing = synthesis.get("missing_params", [])
        missing_prompt = build_missing_params_prompt(structure, missing, fmt=prompt_format)
        missing_schema = build_missing_params_schema(structure, missing) if prompt_format == "json_schema" else None

    def cand_score(candidate: Dict[str, Any]) -> tuple[int, int, int, float]:
        synth = candidate.get("synthesis", {})
        feasible = bool(synth.get("feasible"))
        missing_n = len(synth.get("missing_params", []))
        errors_n = len(synth.get("errors", []))
        return (1 if feasible else 0, -missing_n, -errors_n, float(candidate.get("prob", 0.0)))

    best = sorted(candidates, key=cand_score, reverse=True)[0] if candidates else None

    return {
        "structure": structure,
        "inference_backend": debug.get("inference_backend", "dual_model"),
        "normalized_text": debug.get("normalized_text", text),
        "normalization": debug.get("normalization", {}),
        "normalization_degraded": bool(debug.get("normalization_degraded", False)),
        "scores": scores,
        "params": params,
        "notes": notes,
        "synthesis": synthesis,
        "missing_prompt": missing_prompt,
        "missing_schema": missing_schema,
        "candidates": candidates,
        "graph_candidates": debug.get("graph_candidates", []),
        "best_candidate": best,
    }
