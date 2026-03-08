# External Demo Package 2026-03-08

## Scope

This package is the current external demo baseline for `Geant4-Agent`.
It separates two evaluation tracks:

1. `Structured live casebank v3_24` as the release baseline.
2. `Colloquial-material live casebank v4_24` as the stress set.

## Current Recommendation

- Use the `v3_24` regression as the primary external demo evidence.
- Use the `v4_24` regression as a known-stress appendix.
- Do not present `v4_24` as fully solved yet; it is useful precisely because it exposes remaining material-understanding gaps.

## Evidence Summary

| Track | Dataset | Total | Pass | Pass Rate | Initial Align | Final Align | Missing Reduction | Confirm Success |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | `docs/datasets/casebank/eval_casebank_multiturn_live_v3_24.json` | 24 | 24 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Stress | `docs/datasets/casebank/eval_casebank_multiturn_live_v4_24_colloquial_materials.json` | 24 | 20 | 0.8333 | 0.9167 | 0.9167 | 1.0000 | 1.0000 |

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
- Confirm / reject overwrite behaviour is stable in this set.

### Stress v4_24

- The system remains usable, but the pass rate drops under more colloquial material descriptions.
- Residual failures are concentrated in material canonicalization and, in one case, source-type interpretation.
- This is a coverage issue, not a control-plane or state-machine issue.

## Known Failing Cases in v4_24

| Case | Failure Reasons |
|---|---|
| `MTM14` | expected_final_mismatch:materials.selected_materials.0 |
| `MTM18` | expected_final_mismatch:materials.selected_materials.0 |
| `MTM20` | initial_complete_mismatch, final_complete_mismatch, expected_final_mismatch:materials.selected_materials.0 |
| `MTM24` | initial_complete_mismatch, final_complete_mismatch, expected_final_mismatch:materials.selected_materials.0, expected_final_mismatch:source.type |

## Suggested External Demo Flow

1. Start with one structured Chinese multi-turn case from `v3_24`.
2. Show one structured English multi-turn case from `v3_24`.
3. Show one overwrite-confirm / reject case from `v3_24`.
4. Present `v4_24` as a stress test and explicitly state that colloquial material names are the current main gap.

## Files

### Regression Outputs

- Baseline JSON: `docs/reports/regression/casebank_regression_2026-03-08_001313.json`
- Baseline EN PDF: `docs/reports/regression/casebank_regression_report_en_2026-03-08_001313.pdf`
- Baseline ZH PDF: `docs/reports/regression/casebank_regression_report_zh_2026-03-08_001313.pdf`
- Stress JSON: `docs/reports/regression/v4_24_colloquial_materials/casebank_regression_2026-03-08_102153.json`
- Stress EN PDF: `docs/reports/regression/v4_24_colloquial_materials/casebank_regression_report_en_2026-03-08_102153.pdf`
- Stress ZH PDF: `docs/reports/regression/v4_24_colloquial_materials/casebank_regression_report_zh_2026-03-08_102153.pdf`

### Supporting Documents

- Technical details: `docs/reports/methodology/technical_details_bilingual_2026-03-07.pdf`
- Local deployment guide: `docs/guides/user_guide_local_deployment_bilingual_2026-03-07.pdf`
- Architecture note: `docs/architecture/ARCHITECTURE.md`

## Next Work

1. Improve colloquial material canonicalization.
2. Add explicit material-clarification prompts when user material is ambiguous.
3. Re-run `v4_24` and promote it once it reaches the same reliability band as `v3_24`.
