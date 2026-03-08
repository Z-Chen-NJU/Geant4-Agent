# Live Multi-Turn Regression Report (DeepSeek, 2026-03-07, v3)

## Scope

This run validates the live `LLM-first + Arbiter + Gate` path after the latest P0/P1 fixes:

- conservative uncertainty guard for fuzzy / missing first turns
- user-facing summary filtering for internal metadata paths
- friendly labels for committed material fields
- action-level dialogue templates kept as the only response templating layer

Dataset:

- `docs/eval_casebank_multiturn_live_v2_12.json`

Live config:

- `nlu/bert_lab/configs/deepseek_api.local.json`
- model: `deepseek-chat`

Output artifacts:

- JSON: `docs/casebank_regression_2026-03-07_145107.json`
- EN PDF: `docs/casebank_regression_report_en_2026-03-07_145107.pdf`
- ZH PDF: `docs/casebank_regression_report_zh_2026-03-07_145107.pdf`

## Summary Metrics

- total cases: `12`
- pass count: `12`
- fail count: `0`
- pass rate: `1.0000`
- initial alignment rate: `1.0000`
- final alignment rate: `1.0000`
- llm used rate: `1.0000`
- total turns: `31`
- avg turns per case: `2.58`
- missing reduction rate: `1.0000`
- confirm apply success rate: `1.0000`
- rollback after confirm rate: `0.0000`
- internal leak turn rate: `0.0000`
- repeated assistant case rate: `0.0000`
- stale confirm case rate: `0.0000`

## Delta vs Previous Live Run

Compared with `docs/casebank_regression_2026-03-07_131625.json`:

- pass rate: `0.8333 -> 1.0000`
- final alignment rate: `0.9167 -> 1.0000`
- internal leak turn rate: `0.0625 -> 0.0000`
- stale confirm case rate: stayed at `0.0000`

## What Changed Technically

### 1. Fuzzy first turns are now conservative

The new uncertainty guard prevents the first turn from committing ungrounded geometry / materials / source / output fields when the user explicitly says the request is incomplete or undecided.

Effect:

- no premature completion on fuzzy starts
- no accidental early locks that block later explicit user updates

### 2. User-visible summaries no longer expose internal metadata

The dialogue summary layer now hides internal-only paths in progress / finalize messages, including:

- `geometry.graph_program`
- `geometry.chosen_skeleton`
- `geometry.root_name`
- `physics.backup_physics_list`
- `physics.covered_processes`
- selection-source / selection-reason metadata paths

Effect:

- no internal field leakage in this live run
- completion messages are user-facing rather than implementation-facing

### 3. Material commit regression is resolved

The previous failure where explicit material input could be normalized but not survive commit no longer appears in the live set.

Effect:

- no remaining `materials.selected_materials` drop in the tested workflow
- overwrite / confirm behavior remains stable

## Template Decision

Current conclusion:

- keep the existing **action-level templates**
- do **not** add scenario templates

Reason:

- the current failure modes were orchestration and summary-filter problems, not missing scenario wording
- thin action templates are sufficient as guardrails for:
  - `ask_clarification`
  - `summarize_progress`
  - `confirm_overwrite`
  - `reject_overwrite`
  - `finalize`
- more aggressive templating would reduce flexibility without addressing the real risks

## Remaining Risks

This run is clean, but the evidence base is still limited.

Current limits:

- only `12` live multi-turn cases
- case diversity is good for smoke/live regression, but not yet broad enough for public exposure claims
- live LLM behavior remains stochastic, so a single clean run is necessary but not sufficient

## Readiness Judgment

Current judgment:

- suitable for internal user testing
- suitable for controlled trial use with real prompts
- not yet enough evidence for unrestricted public testing

The next bottleneck is no longer P0 orchestration correctness. The next bottleneck is coverage:

1. expand the live casebank
2. add more fuzzy and adversarial multi-turn cases
3. stress geometry-heavy operator-graph scenarios under live prompting
