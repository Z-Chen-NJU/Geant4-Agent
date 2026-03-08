# External Demo Package 2026-03-08

## Scope

This package is the current external demo baseline for `Geant4-Agent`.
It now retains two demo-grade evaluation tracks:

1. `Structured live casebank v3_24` as the main baseline.
2. `Colloquial-material live casebank v4_24` as the robustness companion set.

## Current Recommendation

- Use `v3_24` as the primary external demo evidence.
- Use `v4_24` immediately after `v3_24` to demonstrate colloquial-material grounding.
- Present `v4_24` as a stress-style companion set that has now passed full live regression, not as an unresolved appendix.

## Evidence Summary

| Track | Dataset | Total | Pass | Pass Rate | Initial Align | Final Align | Missing Reduction | Confirm Success |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | `docs/datasets/casebank/eval_casebank_multiturn_live_v3_24.json` | 24 | 24 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Companion | `docs/datasets/casebank/eval_casebank_multiturn_live_v4_24_colloquial_materials.json` | 24 | 24 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## What Changed in v4

The `v4_24` dataset replaces explicit Geant4 material tags in user utterances with colloquial material names, for example:

- `G4_Fe` -> `?` / `iron`
- `G4_Cu` -> `?` / `copper`
- `G4_WATER` -> `?` / `water`
- `G4_CsI` -> `???` / `cesium iodide`

The expected final configuration still uses canonical Geant4 labels.

## Interpretation

### Baseline v3_24

- The runtime chain is stable enough for controlled external demonstrations.
- Geometry / materials / source / physics / output can close in multi-turn dialogue.
- Confirm / reject overwrite behavior is stable in this set.

### Companion v4_24

- The colloquial-material variant now also closes at `24/24` in live regression.
- This indicates that colloquial material grounding, source-type preservation, and graph-family retention are now stable enough for demonstration use.
- `v4_24` should still be retained as a robustness-oriented companion set because it is stricter than `v3_24`.

## Suggested External Demo Flow

1. Start with one structured Chinese multi-turn case from `v3_24`.
2. Show one structured English multi-turn case from `v3_24`.
3. Show one overwrite-confirm / reject case from `v3_24`.
4. Then show one colloquial-material case from `v4_24` to demonstrate natural-language material grounding.

## Files

### Regression Outputs

- Baseline JSON: `docs/reports/regression/casebank_regression_2026-03-08_001313.json`
- Baseline EN PDF: `docs/reports/regression/casebank_regression_report_en_2026-03-08_001313.pdf`
- Baseline ZH PDF: `docs/reports/regression/casebank_regression_report_zh_2026-03-08_001313.pdf`
- Companion JSON: `docs/reports/regression/v4_24_colloquial_materials/casebank_regression_2026-03-08_124606.json`
- Companion EN PDF: `docs/reports/regression/v4_24_colloquial_materials/casebank_regression_report_en_2026-03-08_124606.pdf`
- Companion ZH PDF: `docs/reports/regression/v4_24_colloquial_materials/casebank_regression_report_zh_2026-03-08_124606.pdf`

### Supporting Documents

- Technical route manual: `docs/demo/technical_route_manual_bilingual_2026-03-08.pdf`
- Technical details: `docs/reports/methodology/technical_details_bilingual_2026-03-07.pdf`
- Local deployment guide: `docs/guides/user_guide_local_deployment_bilingual_2026-03-07.pdf`
- Architecture note: `docs/architecture/ARCHITECTURE.md`

## Next Work

1. Expand the live casebank rather than rewrite the main architecture.
2. Increase adversarial fuzzy cases for geometry-heavy operator-graph scenarios.
3. Tighten the internal-leak metric so it reflects actual user-visible leaks only.
