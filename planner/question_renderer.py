from __future__ import annotations

from planner.agent import ask_missing


def render_question(
    planned_paths: list[str],
    *,
    lang: str,
    ollama_config: str,
    temperature: float,
) -> str:
    return ask_missing(
        planned_paths,
        lang=lang,
        ollama_config=ollama_config,
        temperature=temperature,
    )

