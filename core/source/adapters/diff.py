from __future__ import annotations

from typing import Any

from core.source.adapters.config_fragment import source_spec_to_config_fragment
from core.source.spec import SourceSpec


def diff_source_config_fragment(spec: SourceSpec, legacy_source: dict[str, Any]) -> dict[str, Any]:
    expected = source_spec_to_config_fragment(spec).get("source", {})
    actual = legacy_source if isinstance(legacy_source, dict) else {}
    mismatches: list[dict[str, Any]] = []
    fields = sorted(set(expected.keys()) | set(actual.keys()))
    for field in fields:
        if expected.get(field) != actual.get(field):
            mismatches.append(
                {
                    "field": f"source.{field}",
                    "expected": expected.get(field),
                    "actual": actual.get(field),
                }
            )
    return {
        "matches": not mismatches,
        "mismatches": mismatches,
        "expected_source": expected,
        "legacy_source": actual,
    }
