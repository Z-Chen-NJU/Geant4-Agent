from __future__ import annotations

import argparse
from http.server import HTTPServer

from ui.web.runtime_state import runtime_config_payload
from ui.web.server import Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local desktop bridge for the Chromium UI shell.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()

    runtime = runtime_config_payload()
    print(f"Desktop bridge serving on http://{args.host}:{args.port}")
    print(
        "LLM runtime:",
        f"provider={runtime.get('current_provider', '')};",
        f"path={runtime.get('current_path', '')};",
        f"model={runtime.get('current_model', '')};",
        f"base_url={runtime.get('current_base_url', '')}",
    )
    preflight = runtime.get("model_preflight", {})
    print(
        "Model preflight:",
        f"ready={preflight.get('ready', False)};",
        f"structure_ok={preflight.get('structure', {}).get('ok', False)};",
        f"ner_ok={preflight.get('ner', {}).get('ok', False)}",
    )
    HTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
