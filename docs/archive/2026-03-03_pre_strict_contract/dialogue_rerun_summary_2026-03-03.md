# Dialogue Rerun Summary

- Generated: 2026-03-03T19:09:06
- Archived obsolete pre-rerun reports to `legacy/reports/2026-03-03_pre_rerun/`.
- Current active reports:
  - `docs/bilingual_dialogue_eval_2026-03-03.md`
  - `docs/multiturn_dialogue_eval_2026-03-03.md`
  - `docs/focused_dialogue_regression_2026-03-03.md`

## Full Rerun
- Bilingual suite: 6/10 -> 0/10
- Multi-turn suite: 3/8 -> 0/8
- Bilingual regressions: S1/zh, S2/zh, S4/en, S4/zh, S5/en, S5/zh
- Multi-turn regressions: MT2/en, MT3/en, MT4/en

Interpretation:
- The same archived prompt sets were replayed end-to-end against the current code and the same remote model (`qwen3:14b`).
- Under the current stricter path-level scoping and intent handling, the legacy evaluation matrix regressed to 0 pass on both suites.
- This means the chain fixes solved the targeted issues, but they also tightened the runtime enough that several old ?pass? cases now fail the broader scenario checks.

## Focused Regression
- Focused rerun pass: 3 / 3
- Covered fixes:
  1. Narrow-turn output update no longer triggers false overwrite confirmation.
  2. Chinese modify + confirm commits only after explicit confirmation.
  3. `explain_choice` no longer hijacks update turns at policy level.

## Next Step
- The current bottleneck is no longer the three targeted chain bugs. It is compatibility between the stricter path-level scope filter and the broader legacy scenario prompts.
- The next pass should make pending overwrite field-scoped (not global) and then retune the full scenario matrix against the stricter control layer.
