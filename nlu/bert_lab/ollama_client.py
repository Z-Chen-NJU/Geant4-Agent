from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class OllamaConfig:
    base_url: str
    model: str
    timeout_s: int = 60
    headers: Dict[str, str] | None = None


def load_config(path: str | Path) -> OllamaConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return OllamaConfig(
        base_url=payload.get("base_url", "http://localhost:11434"),
        model=payload.get("model", "llama3"),
        timeout_s=int(payload.get("timeout_s", 60)),
        headers=payload.get("headers", {"Content-Type": "application/json"}),
    )


def chat(
    prompt: str,
    config_path: str | Path = "nlu/bert_lab/configs/ollama_config.json",
    **options: Any,
) -> Dict[str, Any]:
    cfg = load_config(config_path)
    payload = {
        "model": cfg.model,
        "prompt": prompt,
        "stream": False,
        "options": options or {},
    }
    url = cfg.base_url.rstrip("/") + "/api/generate"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=cfg.headers or {})
    with urllib.request.urlopen(req, timeout=cfg.timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_json(text: str) -> Dict[str, Any] | None:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    # Fallback: find first JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            return None
    return None


