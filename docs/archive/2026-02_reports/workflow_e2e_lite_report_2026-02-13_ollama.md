# Workflow E2E Lite Report

- Date: 2026-02-13
- Mode: full workflow (`llm_router=true`, `llm_question=true`, `normalize_input=true`)

## Summary

- Cases: 3
- Workflow accuracy: 0.333
- Average case latency (s): 255.632

## Per Case

| case_id | category | expect_complete | actual_complete | ok | turns | latency_s |
|---|---|---|---|---|---|---|
| lite_complete_one_turn | ideal | True | False | False | 1 | 295.452 |
| lite_two_turn_fill_source | realistic | True | False | False | 2 | 316.988 |
| lite_no_geometry_should_incomplete | stress | False | False | True | 1 | 154.457 |