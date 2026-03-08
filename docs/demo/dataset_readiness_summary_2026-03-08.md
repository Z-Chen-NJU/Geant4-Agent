# Dataset Readiness Summary 2026-03-08

## Scope

This note classifies the current evaluation datasets by demo readiness and recommended usage.
All files listed here are intended to sit beside the main demo package in `docs/demo`.

## Recommendation Summary

| Dataset | Latest Referenced Result | Pass Rate | Readiness | Recommended Use |
|---|---|---:|---|---|
| `eval_casebank_v1_20.json` | archived `2026-03-05_234917` | 1.0000 | Demo-ready | Small static baseline, quick overview |
| `eval_casebank_missing_multiturn_v1_10.json` | archived `2026-03-06_124519` | 1.0000 | Demo-ready | Missing-parameter closure demo |
| `eval_casebank_v2_50.json` | archived `2026-03-06_134702` | 0.9200 | Internal-only | Broad regression, not stable enough for external demo |
| `eval_casebank_multiturn_live_v2_12.json` | archived `2026-03-07_145107` | 1.0000 | Demo-ready | Compact live multi-turn demo |
| `eval_casebank_multiturn_live_v3_24.json` | current `2026-03-08_001313` | 1.0000 | Primary demo baseline | Main external demonstration set |
| `eval_casebank_multiturn_live_v4_24_colloquial_materials.json` | current `2026-03-08_124606` | 1.0000 | Demo-ready companion | Colloquial-material robustness demo |

## Interpretation

### Primary demo sets

Use these externally without caveat:

- `docs/datasets/casebank/eval_casebank_v1_20.json`
- `docs/datasets/casebank/eval_casebank_missing_multiturn_v1_10.json`
- `docs/datasets/casebank/eval_casebank_multiturn_live_v2_12.json`
- `docs/datasets/casebank/eval_casebank_multiturn_live_v3_24.json`
- `docs/datasets/casebank/eval_casebank_multiturn_live_v4_24_colloquial_materials.json`

These sets now support a coherent story:

1. small structured baseline
2. missing-parameter closure
3. compact live multi-turn
4. full live external baseline
5. colloquial-material robustness

### Internal-only set

- `docs/datasets/casebank/eval_casebank_v2_50.json`

This set is useful because it is broad, but its latest retained pass rate is `0.92`, so it is better treated as an engineering regression bank rather than polished demo evidence.

## Suggested demo folder contents

For a clean external handoff, the recommended files in `docs/demo` are:

- `external_demo_package_2026-03-08.md`
- `external_demo_package_bilingual_2026-03-08.pdf`
- `dataset_readiness_summary_2026-03-08.md`
- `dataset_readiness_summary_bilingual_2026-03-08.pdf`
- `technical_route_manual_2026-03-08.md`
- `technical_route_manual_bilingual_2026-03-08.pdf`

## Next promotion target

The next target is no longer `v4_24`; that set is now promoted. The next useful promotion target is a larger adversarial live set that preserves the same closure quality under broader fuzzy language.
