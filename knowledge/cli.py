from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validate import validate_environment_spec, validate_material_spec, validate_min_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate material/environment specs")
    parser.add_argument("--input", required=True, help="JSON file with keys: material_spec, environment_spec")
    parser.add_argument("--materials", default="knowledge/data/materials_geant4_nist.json")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    material_spec = payload.get("material_spec", {})
    environment_spec = payload.get("environment_spec", {})
    min_config = payload.get("min_config", {})

    issues = []
    issues.extend(validate_material_spec(material_spec, args.materials))
    issues.extend(validate_environment_spec(environment_spec))

    issues.extend(validate_min_config(min_config))
    out = {"ok": not any(i.level == "error" for i in issues), "issues": [i.__dict__ for i in issues]}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
