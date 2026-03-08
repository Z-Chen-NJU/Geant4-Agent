from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify eval casebank balance.")
    parser.add_argument(
        "--dataset",
        default="docs/eval_casebank_v1_20.json",
        help="Path to eval casebank JSON file.",
    )
    args = parser.parse_args()

    path = Path(args.dataset)
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    cases = payload.get("cases", [])
    style_counter = Counter()
    completeness_counter = Counter()
    cross_counter = Counter()
    for case in cases:
        style = str(case.get("style", "")).strip().lower()
        completeness = str(case.get("completeness", "")).strip().lower()
        style_counter[style] += 1
        completeness_counter[completeness] += 1
        cross_counter[f"{style}_{completeness}"] += 1

    summary = {
        "total": len(cases),
        "style": dict(style_counter),
        "completeness": dict(completeness_counter),
        "cross_matrix": dict(cross_counter),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
