# Live Multi-Turn Regression Report (DeepSeek, 2026-03-07)

## Scope

This run validates the live `LLM-first + Arbiter + Gate` dialogue path after:

- fixing stale `confirm_overwrite -> finalize` rendering
- adding action-level dialogue templates
- reducing internal-field leakage in user-facing messages
- cleaning and expanding the live multi-turn dataset

Dataset:

- `docs/eval_casebank_multiturn_live_v2_12.json`

Live config:

- `nlu/bert_lab/configs/deepseek_api.local.json`
- model: `deepseek-chat`

Output artifacts:

- JSON: `docs/casebank_regression_2026-03-07_131625.json`
- EN PDF: `docs/casebank_regression_report_en_2026-03-07_131625.pdf`
- ZH PDF: `docs/casebank_regression_report_zh_2026-03-07_131625.pdf`

## Dataset Updates

The live casebank was optimized in two ways:

1. Replaced corrupted Chinese prompts/follow-ups with valid UTF-8 text.
2. Added explicit overwrite confirm/reject coverage.

Affected cases:

- cleaned Chinese cases: `MTM01`, `MTM03`, `MTM05`, `MTM07`, `MTM09`, `MTM12`
- overwrite coverage cases: `MTM11`, `MTM12`

## Summary Metrics

Latest run summary:

- total cases: `12`
- pass count: `10`
- fail count: `2`
- pass rate: `0.8333`
- initial alignment rate: `0.9167`
- final alignment rate: `0.9167`
- llm used rate: `1.0000`
- total turns: `32`
- avg turns per case: `2.67`
- missing reduction rate: `1.0000`
- confirm apply success rate: `1.0000`
- rollback after confirm rate: `0.0000`
- internal leak turn rate: `0.0625`
- repeated assistant case rate: `0.0000`
- stale confirm case rate: `0.0000`

## What Improved

### 1. The stale confirm bug is fixed

This regression no longer shows the previous failure mode where:

- the user replied `confirm`
- internal state became complete
- but the visible assistant action stayed at `confirm_overwrite`

Observed metric:

- `stale_confirm_case_rate = 0.0`

### 2. User-facing leakage dropped significantly

The user-visible layer now leaks internal fields much less often.

Observed metric:

- `internal_leak_turn_rate = 0.0625`

This is materially better than the earlier live run where internal labels were still frequent in assistant turns.

### 3. Overwrite flow is operational

The live path now supports:

- explicit overwrite preview
- explicit user confirmation
- explicit keep-existing / reject handling

Observed metrics:

- `confirm_apply_success_rate = 1.0`
- `rollback_after_confirm_rate = 0.0`
- `repeated_assistant_case_rate = 0.0`

## Remaining Failures

### Failure 1: `MTM05`

Failure reasons:

- `initial_complete_mismatch`
- `missing_not_reduced_after_followups`

Observed behavior:

- the first fuzzy Chinese turn was treated as already complete
- the follow-up then triggered overwrite confirmation for box dimensions

Interpretation:

- this is primarily a **prompt/closure policy issue**
- the system is still too willing to auto-complete fuzzy prompts using defaults

Impact:

- the final config is correct
- but the dialogue state machine reaches `complete` too early for this case

### Failure 2: `MTM06`

Failure reason:

- `final_complete_mismatch`

Observed behavior:

- the follow-up explicitly says `steel cylinder target ...`
- the LLM slot payload correctly normalizes this to `materials.primary = G4_STAINLESS-STEEL`
- but the committed config still ends with:
  - `materials.selected_materials = []`
  - `volume_material_map = {}`

Interpretation:

- this is a real **P0/P1 orchestration bug**, not a dataset problem
- the material update is present in the slot payload, but it is not surviving the explicit-target / arbitration / commit path

Impact:

- the system remains incomplete after user confirmation
- the assistant asks for material binding even though the material was already provided semantically

## Technical Interpretation

Current failure composition is now much narrower than before:

1. Dialogue rendering / overwrite synchronization:
   - largely fixed
2. Dataset corruption:
   - fixed
3. Remaining issues:
   - fuzzy-case early closure
   - material update loss in one live path

This means the next work should not focus on broad dialogue templating first.
The next work should focus on:

- closure policy
- material commit path

## Recommended Next Steps

### P0

1. Fix the material update loss in the `slot_frame -> slot_mapper -> explicit target filter -> arbitration` chain.
2. Add a regression test that asserts:
   - `materials.primary` from slot-style targets survives explicit-target filtering
   - final config contains both:
     - `materials.selected_materials`
     - `materials.volume_material_map`

### P1

1. Tighten closure policy for fuzzy first turns:
   - do not mark a case complete if geometry/material/source/physics/output are only default-filled and not explicitly grounded
2. Add a dedicated live-case regression bucket for:
   - fuzzy-first Chinese
   - fuzzy-first English
   - overwrite-after-fuzzy

## Current Readiness Judgment

This version is suitable for:

- internal testing
- constrained user trials
- iterative debugging with real prompts

It is not yet suitable for:

- open public testing
- claims of stable human-facing multi-turn completion

The reason is now specific and narrow:

- one real material-commit bug remains
- one closure-policy problem remains
