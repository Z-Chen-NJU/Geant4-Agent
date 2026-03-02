# 三类端到端回归报告

- 日期: 2026-02-13
- 流程: user text -> semantic parse -> candidate graph search -> feasibility
- 说明: 本轮为可复现实验，关闭 Ollama 依赖（`normalize_input=false`, `llm_fill_missing=false`）

## 总体结果

- 样例数: 9
- 结构识别准确率: 0.889
- 可行性判定准确率: 1.000

## 分类结果

### ideal
- 样例数: 3
- 结构识别准确率: 1.000
- 可行性判定准确率: 1.000

### realistic
- 样例数: 3
- 结构识别准确率: 1.000
- 可行性判定准确率: 1.000

### stress
- 样例数: 3
- 结构识别准确率: 0.667
- 可行性判定准确率: 1.000

## 逐例结果

| case_id | category | expected_structure | predicted_structure | structure_ok | expected_feasible | predicted_feasible | feasible_ok |
|---|---|---|---|---|---|---|---|
| ideal_polycone_explicit | ideal | single_polycone | single_polycone | True | True | True | True |
| ideal_cuttubs_explicit | ideal | single_cuttubs | single_cuttubs | True | True | True | True |
| ideal_boolean_explicit | ideal | boolean | boolean | True | True | True | True |
| realistic_polycone_natural | realistic | single_polycone | single_polycone | True | True | True | True |
| realistic_cuttubs_natural | realistic | single_cuttubs | single_cuttubs | True | True | True | True |
| realistic_boolean_natural | realistic | boolean | boolean | True | True | True | True |
| stress_ambiguous_layout | stress | unknown | unknown | True | None | None | None |
| stress_no_geometry | stress | unknown | single_box | False | None | True | None |
| stress_infeasible_cuttubs | stress | single_cuttubs | single_cuttubs | True | False | False | True |