# Dataset Refresh Note (2026-03-08)

## Archived
- Archived historical regression bundles to `docs/archive/2026-03-08_regression_history/`.
- Kept the current passing baseline bundle in `docs/` root:
  - `casebank_regression_2026-03-08_001313.json`
  - `casebank_regression_report_en_2026-03-08_001313.tex`
  - `casebank_regression_report_en_2026-03-08_001313.pdf`
  - `casebank_regression_report_zh_2026-03-08_001313.tex`
  - `casebank_regression_report_zh_2026-03-08_001313.pdf`

## New Regression Dataset
- Source dataset: `docs/eval_casebank_multiturn_live_v3_24.json`
- New dataset: `docs/eval_casebank_multiturn_live_v4_24_colloquial_materials.json`
- Change: replaced explicit `G4_*` user-side material mentions with colloquial material names.
- Expected final labels remain canonical Geant4 material names.

## Material Surface Replacements
- Chinese: `G4_Cu -> ?`, `G4_Al -> ?`, `G4_Fe -> ?`, `G4_Pb -> ?`, `G4_Si -> ?`, `G4_WATER -> ?`, `G4_AIR -> ??`, `G4_CsI -> ???`
- English: `G4_Cu -> copper`, `G4_Al -> aluminum`, `G4_Fe -> iron`, `G4_Pb -> lead`, `G4_Si -> silicon`, `G4_WATER -> water`, `G4_AIR -> air`, `G4_CsI -> cesium iodide`

## Validation
- Dataset structure verified with `scripts/verify_eval_casebank.py`.
- Prompt/follow-up user text no longer contains explicit `G4_*` material tokens.

## Next Step
- Run live regression on `eval_casebank_multiturn_live_v4_24_colloquial_materials.json`.
- Use the new passing result as the basis for external demo materials.
