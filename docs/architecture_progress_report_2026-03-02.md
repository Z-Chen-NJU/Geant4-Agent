# Architecture Progress Report (2026-03-02)

## Scope
This round completed three items:
1. Clean legacy UI-facing text in `ui/web/legacy_api.py`.
2. Continue extracting reusable runtime modules out of `nlu/bert_lab`.
3. Attempt a real strict-path Ollama end-to-end regression.

## Code Changes

### 1. Legacy text cleanup
The following legacy user-facing text paths were cleaned:
- `ui/web/legacy_api.py`
  - `_friendly_fields(...)`
  - `_ask_llm(...)`
  - Chinese physics recommendation token lists

Result:
- Legacy phase labels are readable.
- Legacy fallback prompt text is readable.
- Legacy field labels are readable.
- A grep scan for common mojibake fragments returned no matches after the cleanup.

### 2. Runtime component extraction
A new reusable runtime package was added:
- `nlu/runtime_components/__init__.py`
- `nlu/runtime_components/graph_search.py`
- `nlu/runtime_components/infer.py`
- `nlu/runtime_components/postprocess.py`

Active imports were switched to the new package:
- `nlu/runtime_semantic.py`
- `nlu/bert_lab/semantic.py`

Current state:
- Strict runtime now uses `nlu.runtime_components.*` instead of importing these helpers directly from `nlu.bert_lab.*`.
- The old `nlu/bert_lab` copies still exist, but the active path no longer depends on them as its import source.

### 3. Strict planner state upgrade (already integrated this round)
The strict planner now tracks retry count per unresolved field.
- `core/orchestrator/types.py`
  - `SessionState.question_attempts`
- `planner/question_planner.py`
  - `update_question_attempts(...)`
  - retry-aware prioritization in `plan_questions(...)`
- `core/orchestrator/session_manager.py`
  - returns `question_attempts`

Effect:
- Repeatedly asked unresolved fields are deprioritized if alternative fields remain.

### 4. Strict router semantics
The strict path now treats `llm_router` as a real control flag.
- `core/validation/error_codes.py`
  - added `E_LLM_ROUTER_DISABLED`
- `core/orchestrator/session_manager.py`
  - `llm_router=False` + `normalize_input=True` skips LLM-first and reports `E_LLM_ROUTER_DISABLED`
  - `normalize_input=False` still reports `E_LLM_DISABLED`

## Validation

### Static compile checks
Successful `py_compile` checks were run for:
- `ui/web/legacy_api.py`
- `nlu/runtime_semantic.py`
- `nlu/runtime_components/graph_search.py`
- `nlu/runtime_components/infer.py`
- `nlu/runtime_components/postprocess.py`
- `nlu/bert_lab/semantic.py`

### Unit / smoke tests
Command:

```powershell
.\.venv\Scripts\python -m unittest tests.test_request_router tests.test_question_planner tests.test_turn_transaction tests.test_llm_semantic_frame tests.test_smoke_no_ollama -v
```

Result:
- `Ran 16 tests`
- `OK`

## Strict Ollama E2E Probe

### Runtime probe
A direct probe to the configured Ollama endpoint failed:

- Target: `http://localhost:11434/api/tags`
- Result: connection failure (`unable to connect to remote server`)

This means a real online Ollama regression could not be completed in this environment because the local Ollama service is not reachable at the configured address.

### Strict-path fallback behavior under unreachable Ollama
A strict two-turn probe was still executed with:
- `strict_mode=True`
- `llm_router=True`
- `normalize_input=True`

Observed result:
- Turn 1:
  - `llm_used = false`
  - `fallback_reason = E_LLM_FRAME_CALL_FAILED`
  - `inference_backend = runtime_semantic`
- Turn 2:
  - `llm_used = false`
  - `fallback_reason = E_LLM_FRAME_CALL_FAILED`
  - strict session continued and reduced missing fields through fallback extraction

Interpretation:
- The strict workflow is stable when Ollama is unreachable.
- The LLM-first path attempts to call Ollama and fails cleanly.
- The system falls back to the deterministic extraction path instead of breaking the session.

## Architecture Status

### Completed
- P0 architecture work is effectively complete.
- Web layer is split into:
  - `ui/web/server.py`
  - `ui/web/request_router.py`
  - `ui/web/strict_api.py`
  - `ui/web/runtime_state.py`
  - `ui/web/legacy_api.py`
- Strict orchestrator has:
  - transactional updates
  - producer separation
  - lock discipline
  - stateful question planning
  - observable router semantics
- Active semantic runtime is separated from the old `nlu/bert_lab/semantic.py` monolith.

### Remaining debt
1. A real online Ollama regression still needs to be rerun once `http://localhost:11434` is reachable.
2. `nlu/bert_lab` still contains duplicate copies of some migrated helpers; strict runtime no longer depends on them directly, but the directory is not fully normalized.
3. `ui/web/legacy_api.py` remains a compatibility layer; if legacy mode is no longer needed, it can be archived further.
4. The current planner is retry-aware but still not fully policy-rich (no hard cap / escalation policy yet).

## Recommended Next Steps
1. Bring Ollama online on `http://localhost:11434` and rerun a strict multi-turn regression.
2. Decide whether `ui/web/legacy_api.py` remains supported or is moved deeper into `legacy/`.
3. If legacy support remains, remove duplicate runtime helper copies from `nlu/bert_lab` by converting them to thin wrappers or deprecating them explicitly.
