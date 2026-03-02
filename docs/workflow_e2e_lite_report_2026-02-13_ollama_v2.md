# Workflow E2E Lite Report

- Date: 2026-02-14
- Mode: full workflow (`llm_router=true`, `llm_question=true`, `normalize_input=true`)

## Summary

- Cases: 3
- Workflow accuracy: 1.000
- Average case latency (s): 240.182

## Per Case

| case_id | category | expect_complete | actual_complete | ok | turns | latency_s |
|---|---|---|---|---|---|---|
| lite_complete_one_turn | ideal | True | True | True | 1 | 194.298 |
| lite_two_turn_fill_source | realistic | True | True | True | 2 | 366.595 |
| lite_no_geometry_should_incomplete | stress | False | False | True | 1 | 159.652 |