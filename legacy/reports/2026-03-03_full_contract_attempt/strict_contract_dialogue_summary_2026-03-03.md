# Strict Contract Dialogue Evaluation Summary

- Date: 2026-03-03
- Base URL: `http://114.212.130.6:11434`
- Model: `qwen3:14b`

## Results
- Bilingual strict-contract suite: `5/10`
- Multiturn strict-contract suite: `6/8`

## Interpretation
- These suites use the new strict turn contract rather than the archived wide-fill prompts.
- Failures here are more representative of current strict runtime behavior.
- If these suites pass while the archived suites fail, the issue is prompt-contract mismatch rather than immediate runtime instability.

## Bilingual Failures
- `S1_EN`: ['final turn not complete']
- `S2_EN`: ['final turn not complete', 'geometry.structure != single_tubs', 'child_rmax != 30', 'child_hz != 50']
- `S2_ZH`: ['final turn not complete', 'geometry.structure != single_tubs', 'child_rmax != 30', 'child_hz != 50']
- `S3_EN`: ['setup turn not complete', 'final action != explain_choice']
- `S3_ZH`: ['final action != explain_choice']

## Multiturn Failures
- `MT3_EN`: ['setup turn not complete', 'final action != explain_choice']
- `MT3_ZH`: ['final action != explain_choice']
