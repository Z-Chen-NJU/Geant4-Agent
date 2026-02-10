from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from nlu.bert_lab.infer import extract_params, predict_structure
from nlu.bert_lab.llm_bridge import build_missing_params_prompt, build_missing_params_schema
from nlu.bert_lab.ollama_client import chat, extract_json
from nlu.bert_lab.postprocess import merge_params
from builder.geometry.synthesize import synthesize_from_params


ROOT = Path(__file__).parent
KNOWLEDGE_DIR = ROOT.parent.parent / "knowledge" / "data"


@dataclass
class SessionState:
    history: List[Dict[str, str]] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    missing_fields: List[str] = field(default_factory=list)
    last_question: str = ""


SESSIONS: Dict[str, SessionState] = {}


def _respond(handler: BaseHTTPRequestHandler, code: int, payload: Dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _load_file(path: Path) -> bytes:
    return path.read_bytes()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_knowledge() -> Dict[str, List[str]]:
    materials = _load_json(KNOWLEDGE_DIR / "materials_geant4_nist.json").get("materials", [])
    physics_lists = _load_json(KNOWLEDGE_DIR / "physics_lists.json").get("items", [])
    particles = _load_json(KNOWLEDGE_DIR / "particles.json").get("items", [])
    sources = _load_json(KNOWLEDGE_DIR / "source_constraints.json").get("types", [])
    if not sources:
        sources = ["point", "beam", "plane", "isotropic"]
    output_formats = _load_json(KNOWLEDGE_DIR / "output_formats.json").get("items", [])
    return {
        "materials": materials,
        "physics_lists": physics_lists,
        "particles": particles,
        "sources": sources,
        "output_formats": output_formats,
    }


KNOWLEDGE = _load_knowledge()


def _match_any(text: str, items: List[str]) -> Optional[str]:
    low = text.lower()
    for item in items:
        if item and item.lower() in low:
            return item
    return None


def _default_config() -> Dict[str, Any]:
    return {
        "geometry": {
            "structure": None,
            "params": {},
            "dsl": None,
            "feasible": None,
            "errors": [],
        },
        "materials": {
            "selected_materials": [],
            "volume_material_map": {},
        },
        "source": {
            "type": None,
            "particle": None,
            "energy": None,
            "position": None,
            "direction": None,
        },
        "physics": {
            "physics_list": None,
        },
        "environment": {
            "temperature": None,
            "pressure": None,
        },
        "output": {
            "format": None,
        },
        "notes": [],
    }


def _ensure_session(session_id: Optional[str]) -> Tuple[str, SessionState]:
    if session_id and session_id in SESSIONS:
        return session_id, SESSIONS[session_id]
    sid = session_id or str(uuid.uuid4())
    SESSIONS[sid] = SessionState(config=_default_config())
    return sid, SESSIONS[sid]


def _heuristic_focus(text: str) -> List[str]:
    low = text.lower()
    focus = []
    geom_keys = ["box", "tubs", "ring", "grid", "stack", "nest", "shell", "cylinder", "sphere"]
    if any(k in low for k in geom_keys):
        focus.append("geometry")
    if any(k in low for k in ["material", "steel", "aluminum", "g4_"]):
        focus.append("materials")
    if any(k in low for k in ["source", "beam", "gamma", "electron", "proton", "neutron"]):
        focus.append("source")
    if any(k in low for k in ["physics list", "ftfp", "qgsp", "qb"]):
        focus.append("physics")
    return focus or ["geometry"]


def _infer_geometry_hint(text: str) -> Optional[str]:
    low = text.lower()
    if any(k in low for k in ["cube", "box", "立方体", "长方体"]):
        return "single_box"
    if any(k in low for k in ["cylinder", "tubs", "圆柱"]):
        return "single_tubs"
    return None


def _route_with_llm(text: str, missing_fields: List[str]) -> Dict[str, Any]:
    prompt = (
        "You are a router that decides which modules to run next in a Geant4 config builder.\n"
        "Return JSON with keys: use_geometry_bert (bool), focus (list of strings: geometry, materials, source, physics), "
        "geometry_hint (optional: single_box or single_tubs), reason (string).\n"
        f"User text: {text}\n"
        f"Missing fields: {missing_fields}\n"
        "JSON:"
    )
    try:
        resp = chat(prompt, config_path="nlu/bert_lab/configs/ollama_config.json", temperature=0.0)
        parsed = extract_json(resp.get("response", "")) or {}
        if isinstance(parsed, dict) and "focus" in parsed:
            return parsed
    except Exception:
        return {}
    return {}


def _decide_focus(text: str, missing_fields: List[str], llm_router: bool) -> Dict[str, Any]:
    if llm_router:
        routed = _route_with_llm(text, missing_fields)
        if routed:
            return routed
    focus = _heuristic_focus(text)
    hint = _infer_geometry_hint(text)
    return {
        "use_geometry_bert": "geometry" in focus,
        "focus": focus,
        "geometry_hint": hint,
        "reason": "heuristic",
    }


def _update_geometry(
    config: Dict[str, Any],
    text: str,
    min_conf: float,
    autofix: bool,
    geometry_hint: Optional[str],
) -> Dict[str, Any]:
    structure, scores, ranked = predict_structure(text, "nlu/bert_lab/models/structure", "auto", min_conf)
    params = extract_params(text, "nlu/bert_lab/models/ner", "auto")
    params, notes = merge_params(text, params)

    config["notes"].extend(notes)
    if structure == "unknown" and geometry_hint:
        structure = geometry_hint
    config["geometry"]["structure"] = None if structure == "unknown" else structure
    config["geometry"]["params"] = params

    if structure != "unknown":
        synth = synthesize_from_params(structure, params, seed=7, apply_autofix=autofix)
        config["geometry"]["dsl"] = synth.get("dsl")
        config["geometry"]["feasible"] = synth.get("feasible")
        config["geometry"]["errors"] = synth.get("errors", [])
        config["geometry"]["missing_params"] = synth.get("missing_params", [])
        config["geometry"]["scores"] = scores
        config["geometry"]["ranked"] = ranked
    else:
        config["geometry"]["dsl"] = None
        config["geometry"]["feasible"] = None
        config["geometry"]["errors"] = ["structure confidence below threshold"]
        config["geometry"]["missing_params"] = []
        config["geometry"]["scores"] = scores
        config["geometry"]["ranked"] = ranked
    return config


def _update_non_geometry(config: Dict[str, Any], text: str) -> Dict[str, Any]:
    mat = _match_any(text, KNOWLEDGE["materials"])
    if mat and mat not in config["materials"]["selected_materials"]:
        config["materials"]["selected_materials"].append(mat)

    phys = _match_any(text, KNOWLEDGE["physics_lists"])
    if phys:
        config["physics"]["physics_list"] = phys

    particle = _match_any(text, KNOWLEDGE["particles"])
    if particle:
        config["source"]["particle"] = particle

    source_type = _match_any(text, KNOWLEDGE["sources"])
    if source_type:
        config["source"]["type"] = source_type

    out_fmt = _match_any(text, KNOWLEDGE["output_formats"])
    if out_fmt:
        config["output"]["format"] = out_fmt

    return config


def _compute_missing(config: Dict[str, Any]) -> List[str]:
    missing = []
    if not config["geometry"]["structure"]:
        missing.append("geometry.structure")
    if config["geometry"].get("structure") and config["geometry"].get("missing_params"):
        for p in config["geometry"]["missing_params"]:
            missing.append(f"geometry.params.{p}")
    if not config["materials"]["selected_materials"]:
        missing.append("materials.selected_materials")
    if not config["source"]["particle"]:
        missing.append("source.particle")
    if not config["source"]["type"]:
        missing.append("source.type")
    if not config["physics"]["physics_list"]:
        missing.append("physics.physics_list")
    if not config["output"]["format"]:
        missing.append("output.format")
    return missing


def _build_user_friendly(config: Dict[str, Any]) -> str:
    geo = config["geometry"]
    return "\n".join(
        [
            f"Geometry: {geo.get('structure') or 'unknown'}",
            f"Feasible: {geo.get('feasible')}",
            f"Materials: {', '.join(config['materials']['selected_materials']) or 'missing'}",
            f"Particle: {config['source']['particle'] or 'missing'}",
            f"Source type: {config['source']['type'] or 'missing'}",
            f"Physics list: {config['physics']['physics_list'] or 'missing'}",
            f"Output format: {config['output']['format'] or 'missing'}",
        ]
    )


def _friendly_missing(missing: List[str], lang: str) -> List[str]:
    if lang == "en":
        mapping = {
            "geometry.structure": "geometry structure (box / ring / grid / stack / shell)",
            "materials.selected_materials": "materials (e.g., G4_WATER / G4_Al / G4_Si)",
            "source.particle": "particle type (gamma / e- / proton)",
            "source.type": "source type (point / beam / isotropic)",
            "physics.physics_list": "physics list (e.g., FTFP_BERT)",
            "output.format": "output format (root / csv / json)",
        }
    else:
        mapping = {
            "geometry.structure": "几何结构（如 box / ring / grid / stack / shell）",
            "materials.selected_materials": "材料（如 G4_WATER / G4_Al / G4_Si）",
            "source.particle": "粒子类型（如 gamma / e- / proton）",
            "source.type": "源类型（如 point / beam / isotropic）",
            "physics.physics_list": "物理过程列表（如 FTFP_BERT）",
            "output.format": "输出格式（如 root / csv / json）",
        }
    friendly = []
    for item in missing:
        if item.startswith("geometry.params."):
            key = item.split("geometry.params.", 1)[1]
            friendly.append(f"geometry parameter {key}" if lang == "en" else f"几何参数 {key}")
        else:
            friendly.append(mapping.get(item, item))
    return friendly


def _ask_llm(missing: List[str], history: List[Dict[str, str]], lang: str) -> str:
    if not missing:
        return ""
    friendly = _friendly_missing(missing, lang)
    if lang == "en":
        prompt = (
            "You are a research assistant. Ask a concise, friendly clarification question in English. "
            "Avoid internal field names.\n"
            f"Missing items: {friendly}\n"
            "Question:"
        )
    else:
        prompt = (
            "你是一个科研助手，请用自然、友好的中文向用户追问缺失信息。"
            "尽量合并成一句话，避免工程化字段名。\n"
            f"缺失内容: {friendly}\n"
            "问题："
        )
    try:
        resp = chat(prompt, config_path="nlu/bert_lab/configs/ollama_config.json", temperature=0.2)
        text = resp.get("response", "").strip()
        if text:
            return text
        return f"Please provide: {', '.join(friendly)}" if lang == "en" else f"请补充：{', '.join(friendly)}"
    except Exception:
        return f"Please provide: {', '.join(friendly)}" if lang == "en" else f"请补充：{', '.join(friendly)}"


def step(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    session_id = payload.get("session_id")
    llm_router = bool(payload.get("llm_router", True))
    min_conf = float(payload.get("min_confidence", 0.6))
    autofix = bool(payload.get("autofix", False))
    lang = str(payload.get("lang", "zh")).lower()

    sid, state = _ensure_session(session_id)
    if not text:
        return {"error": "missing text", "session_id": sid}

    state.history.append({"role": "user", "content": text})
    routed = _decide_focus(text, state.missing_fields, llm_router)

    if routed.get("use_geometry_bert", True):
        state.config = _update_geometry(
            state.config,
            text,
            min_conf,
            autofix,
            routed.get("geometry_hint") or _infer_geometry_hint(text),
        )

    state.config = _update_non_geometry(state.config, text)
    state.missing_fields = _compute_missing(state.config)

    question = _ask_llm(state.missing_fields, state.history, lang)
    if question:
        state.history.append({"role": "assistant", "content": question})
        state.last_question = question
    else:
        state.last_question = ""

    return {
        "session_id": sid,
        "router": routed,
        "missing_fields": state.missing_fields,
        "assistant_message": question or "Configuration complete.",
        "display": _build_user_friendly(state.config),
        "config": state.config,
        "history": state.history[-10:],
    }


def solve(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        return {"error": "missing text"}

    top_k = int(payload.get("top_k", 1))
    min_conf = float(payload.get("min_confidence", 0.6))
    prompt_format = payload.get("prompt_format", "json_schema")
    autofix = bool(payload.get("autofix", False))
    llm_fill = bool(payload.get("llm_fill_missing", False))
    params_override = payload.get("params_override", {}) or {}

    structure, scores, ranked = predict_structure(text, "nlu/bert_lab/models/structure", "auto", min_conf)
    params = extract_params(text, "nlu/bert_lab/models/ner", "auto")
    params, notes = merge_params(text, params)
    params.update(params_override)

    candidates = []
    for name, prob in ranked[: max(1, top_k)]:
        if prob < min_conf:
            continue
        synth = synthesize_from_params(name, params, seed=7, apply_autofix=autofix)
        missing = synth.get("missing_params", [])
        prompt = build_missing_params_prompt(name, missing, fmt=prompt_format)
        schema = build_missing_params_schema(name, missing) if prompt_format == "json_schema" else None
        filled = None
        if llm_fill and missing:
            resp = chat(prompt, config_path="nlu/bert_lab/configs/ollama_config.json", temperature=0.2)
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

    def _cand_score(c):
        synth = c.get("synthesis", {})
        feasible = bool(synth.get("feasible"))
        missing_n = len(synth.get("missing_params", []))
        errors_n = len(synth.get("errors", []))
        return (1 if feasible else 0, -missing_n, -errors_n, c.get("prob", 0.0))

    best = None
    if candidates:
        best = sorted(candidates, key=_cand_score, reverse=True)[0]

    return {
        "structure": structure,
        "scores": scores,
        "params": params,
        "notes": notes,
        "synthesis": synthesis,
        "missing_prompt": missing_prompt,
        "missing_schema": missing_schema,
        "candidates": candidates,
        "best_candidate": best,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.strip("/")
        if path == "":
            data = _load_file(ROOT / "index.html")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path in {"style.css", "app.js"}:
            data = _load_file(ROOT / path)
            mime = "text/css" if path.endswith(".css") else "application/javascript"
            self.send_response(200)
            self.send_header("Content-Type", f"{mime}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path not in {"/api/solve", "/api/step", "/api/reset"}:
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            _respond(self, 400, {"error": "invalid json"})
            return
        if self.path == "/api/solve":
            out = solve(payload)
        elif self.path == "/api/reset":
            session_id = payload.get("session_id")
            if session_id in SESSIONS:
                del SESSIONS[session_id]
            out = {"ok": True}
        else:
            out = step(payload)
        _respond(self, 200, out)


def main() -> None:
    host = "127.0.0.1"
    port = 8088
    print(f"Serving on http://{host}:{port}")
    HTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()






