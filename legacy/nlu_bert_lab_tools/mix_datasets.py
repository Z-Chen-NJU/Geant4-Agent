from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def load_jsonl(path: str) -> List[Dict[str, object]]:
    p = Path(path)
    if not p.exists():
        return []
    items: List[Dict[str, object]] = []
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        items.append(json.loads(line))
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Mix LLM and synthetic JSONL datasets")
    parser.add_argument("--llm", required=True, help="LLM JSONL path")
    parser.add_argument("--synthetic", required=True, help="Synthetic JSONL path")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    args = parser.parse_args()

    llm_items = load_jsonl(args.llm)
    syn_items = load_jsonl(args.synthetic)
    out = Path(args.out)

    merged: List[Dict[str, object]] = []
    for src in (llm_items, syn_items):
        for obj in src:
            merged.append(
                {
                    "text": obj.get("text", ""),
                    "structure": obj.get("structure", ""),
                    "params": obj.get("params", {}),
                }
            )

    out.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in merged) + "\n", encoding="utf-8")
    print(f"merged={len(merged)} llm={len(llm_items)} synthetic={len(syn_items)}")


if __name__ == "__main__":
    main()


