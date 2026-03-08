# Live Multi-Turn Regression Report - 2026-03-07

## Run Metadata

- Dataset: `docs/eval_casebank_missing_multiturn_v1_10.json`
- Config: `nlu/bert_lab/configs/deepseek_api.local.json`
- Provider: `deepseek`
- Model: `deepseek-chat`
- JSON report: `docs/casebank_regression_2026-03-07_113802.json`
- EN PDF: `docs/casebank_regression_report_en_2026-03-07_113802.pdf`
- ZH PDF: `docs/casebank_regression_report_zh_2026-03-07_113802.pdf`

## Headline Results

- Pass rate: `0.90` (9/10)
- Initial alignment rate: `0.90`
- Final alignment rate: `1.00`
- LLM used rate: `1.00`
- Missing reduction rate: `1.00`
- Confirm apply success rate: `1.00`
- Rollback after confirm rate: `0.00`

## Quantitative Diagnostics

- Total turns: `23`
- Average turns per case: `2.3`
- Average initial missing count: `9.5`
- Average final missing count: `0.0`
- Turns with internal field leakage in user-facing assistant text: `7/23` (`30.4%`)
- Cases with repeated assistant message on consecutive turns: `1/10` (`10%`)
- Cases with `is_complete=true` but `dialogue_action=confirm_overwrite`: `3` (`MTM02`, `MTM06`, `MTM08`)
- Chinese prompt corruption in dataset: `5/10` cases (`MTM01`, `MTM03`, `MTM05`, `MTM07`, `MTM09`)

## Per-Case Outcomes

| Case | Domain | Style | Lang | Turns | Result | Notes |
|---|---|---|---:|---:|---|---|
| MTM01 | medical | fuzzy | zh | 2 | PASS | OK |
| MTM02 | aerospace | precise | en | 3 | PASS | state/message mismatch after confirm |
| MTM03 | industrial_ndt | precise | zh | 2 | PASS | OK |
| MTM04 | physics | precise | en | 2 | PASS | OK |
| MTM05 | nuclear_engineering | fuzzy | zh | 2 | PASS | OK |
| MTM06 | security_screening | fuzzy | en | 3 | FAIL | initial_complete_mismatch; missing_not_reduced_after_followups |
| MTM07 | semiconductor | precise | zh | 2 | PASS | OK |
| MTM08 | education | fuzzy | en | 3 | PASS | state/message mismatch after confirm |
| MTM09 | environmental_radiation | fuzzy | zh | 2 | PASS | OK |
| MTM10 | high_energy_physics | precise | en | 2 | PASS | OK |

## Key Findings

### 1. Semantic closure is strong

- Final alignment reached `1.00` even under live API execution.
- Every case ended with `final_missing_count=0`.
- The single failed case did **not** fail because the final config was wrong. It failed because turn-level control flow and completion accounting were inconsistent.

### 2. There is still a P0 dialogue-state bug after overwrite confirmation

- In `MTM02`, `MTM06`, and `MTM08`, the system marks the turn as complete after the user says `confirm`, but the user-facing response is still a `confirm_overwrite` prompt.
- This is not a natural-language problem. It is a state/action/render synchronization bug.
- As long as this exists, public testing is risky because the user sees the system asking for confirmation **again** after confirmation has already been applied.

### 3. User-facing naturalization is improved but not clean enough

- Internal field leakage is still visible in `30.4%` of assistant turns.
- Typical leaks: `module_x`, `module_y`, `child_rmax`, `materials.selected_materials`.
- This means the response rewrite layer is not yet enforcing a strict enough final surface contract.

### 4. The current multi-turn dataset is partially invalid for Chinese UX evaluation

- `5/10` cases contain corrupted Chinese prompts/followups encoded as `?` characters in the dataset itself.
- Because of that, this run is valid for logic and closure evaluation, but only partially valid for Chinese naturalness evaluation.

### 5. Default-first behavior is still too aggressive in one scenario

- `MTM06` begins with a very vague prompt: `Need a quick cargo-screening toy setup with forward photons; details can follow.`
- The system still finalized the first turn immediately instead of holding an incomplete state and asking for the essential missing items.
- This indicates the system is still over-committing under vague prompts in at least one branch.

## Representative Dialogues

### Case MTM04 - Good Multi-Turn Behavior

User: `Gamma point source 1 MeV at (0,0,-100) toward +z; please build the rest.`

Assistant:

> Great, we've set up your source: a 1 MeV gamma point source at (0,0,-100) directed along +Z.
>
> To finish the configuration, we still need:
> * Geometry: The structure type and its X dimension.
> * Materials: Which material to assign to the volume.
> * Physics: The physics list to use.
> * Output: The format and file path for your results.

User: `Set copper box 1 m x 1 m x 1 m, physics FTFP_BERT, output hdf5.`

Assistant: `Your configuration is complete.`

Assessment:

- This is the target interaction style: concise, natural, minimal, and semantically correct.
- No overwrite issue appears here.

### Case MTM06 - Control-Flow Failure Under Live API

User: `Need a quick cargo-screening toy setup with forward photons; details can follow.`

Assistant: `Your configuration is complete.`

User: `Use steel cylinder target radius 60 mm half-length 120 mm, beam gamma 3 MeV from (0,0,-500) mm to +z, physics Shielding, output root.`

Assistant: asks for overwrite confirmation on geometry and material.

User: `confirm`

Assistant: asks for the **same overwrite confirmation again**.

Assessment:

- This is the main live failure in the run.
- The system logic says the session is complete, but the rendered assistant message still behaves as if confirmation is pending.

### Case MTM10 - Naturalness Still Leaks Internal Terms

Assistant first-turn message included: `The sphere's maximum radius (child_rmax).`

Assessment:

- This is understandable for developers, but not acceptable as final user-facing phrasing.
- The correct surface form should be something like `the sphere radius`.

## Template Decision

### Do we need templates?

Yes, but not as hardcoded end-to-end dialogue scripts.

What is needed is a **thin response-template layer** for the final user-facing rendering of high-risk actions:

- `ask_clarification`
- `summarize_progress`
- `confirm_overwrite`
- `reject_overwrite`
- `finalize`
- `answer_status`

### Why

- The live run shows that the core semantic extraction is already usable.
- The remaining problems are concentrated at the **response surface**: stale confirmation text, internal field leakage, and inconsistent wording.
- A thin template layer will stabilize the output without undoing the LLM-first architecture.

### What kind of templates

- Not per-scenario templates.
- Not full scripted conversations.
- Use **action templates with slots**, for example:
  - overwrite diff list
  - missing field group list
  - confirmed update summary
  - completion summary
- Let the LLM optionally paraphrase **inside** those boundaries, but never own the final contract.

### Priority

1. Fix state/action/render synchronization after confirm.
2. Enforce friendly-label rendering so internal fields cannot leak into final user text.
3. Add action-level response templates as the final render contract.
4. Rebuild the corrupted Chinese multi-turn dataset before using live runs as a Chinese UX benchmark.

## Recommendation

- Do **not** treat this run as public-beta ready for multi-turn dialogue.
- Treat it as `logic mostly ready, UX layer not yet hardened`.
- The next iteration should focus on the renderer contract, not on BERT retraining.