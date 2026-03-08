# Geant4-Agent 技术细节报告

## 1. 当前状态

截至 `2026-03-07`，项目的核心主链已经基本稳定：

- `LLM-first` 标准化已接入正式运行链路
- `BERT` 已降级为先验与补充，不再拥有主导提交权
- `Arbiter + Validator Gate` 已成为唯一提交通道
- `overwrite / confirm / reject` 多轮控制链路已经闭环
- 用户层内部字段泄漏在最新 live 回归中已降到 `0.0`

当前阶段的主要工作重心，已经从“架构纠错”转向“覆盖度扩展”。

---

## 2. 系统目标

项目当前目标不是直接生成完整 Geant4 工程，而是先稳定完成一个 **first-pass 配置闭环系统**，覆盖：

- `geometry`
- `materials`
- `source`
- `physics`
- `output`

同时满足以下硬约束：

1. `LLM/BERT` 只能产出候选，不能直接写入配置
2. 会话态 `config` 是唯一真值源
3. 所有更新必须经过 `Arbiter + Gate`
4. 几何优先使用通用算子和 graph program，而不是场景模板类
5. 未经用户明确同意，不覆盖已确认内容

---

## 3. 当前架构分层

### 3.1 目录分层

- `builder/geometry/`
  - 几何 DSL、理论可行性验证、graph skeleton、参数合成
- `core/`
  - 会话编排、路径处理、锁账本、字段注册、验证、对话状态
- `nlu/`
  - LLM 标准化、slot frame、BERT prior、runtime semantic 解析
- `planner/`
  - 澄清问题规划、用户层话术自然化
- `knowledge/`
  - 材料等知识数据
- `ui/web/`
  - 本地 Web UI
- `scripts/`
  - 回归、训练、数据集构建

### 3.2 运行主入口

当前运行主入口是：

- `ui/web/server.py`
- `core/orchestrator/session_manager.py`

Web UI 收到用户输入后，最终会进入 `process_turn(...)` 完成一轮严格处理。

---

## 4. 单轮处理链路

### 4.1 输入阶段

用户输入从以下链路进入：

- `ui/web/server.py`
- `ui/web/request_router.py`
- `ui/web/strict_api.py`
- `core/orchestrator/session_manager.py`

主要开关包括：

- `llm_router`
- `llm_question`
- `normalize_input`
- `autofix`
- `strict_mode`

### 4.2 LLM-first 标准化

标准化相关文件：

- `nlu/llm/normalizer.py`
- `nlu/llm/slot_frame.py`
- `nlu/llm/semantic_frame.py`

这一层的职责是：

- 识别意图：`SET / MODIFY / REMOVE / CONFIRM / REJECT / QUESTION`
- 提取结构化 slot frame
- 推断 target paths
- 输出可供后续链路使用的标准化结果

重要约束：

- 这一层只有提案权
- 不具备直接提交配置的权限

### 4.3 不确定性抑制

新增的不确定性模块：

- `nlu/uncertainty.py`

它会识别类似：

- “还没定”
- “先给一个缺参开头”
- “not fixed yet”
- “unspecified”
- “undecided”

如果首轮明确表示信息未定，则系统会：

- 清掉未被原文锚定的字段
- 将意图保守降级为 `QUESTION`
- 防止错误完成
- 防止错误加锁

这一步修复了之前 fuzzy 首轮过早 complete 的问题。

### 4.4 BERT prior 与 runtime semantic

相关文件：

- `nlu/runtime_components/infer.py`
- `nlu/runtime_semantic.py`
- `nlu/bert/extractor.py`

当前 BERT 的角色是：

- 给出 structure prior
- 作为规则恢复的补充信号
- 在 LLM 不稳定时提供保守先验

当前不再采用“先分类 structure，再强灌参数”的旧路线。

### 4.5 几何合成与 graph search

相关文件：

- `builder/geometry/dsl.py`
- `builder/geometry/geom.py`
- `builder/geometry/feasibility.py`
- `builder/geometry/library.py`
- `builder/geometry/synthesize.py`
- `nlu/runtime_components/graph_search.py`

当前已接入主链的单体 family 包括：

- `single_box`
- `single_tubs`
- `single_sphere`
- `single_orb`
- `single_cons`
- `single_trd`
- `single_polycone`
- `single_cuttubs`
- `single_trap`
- `single_para`
- `single_torus`
- `single_ellipsoid`
- `single_elltube`
- `single_polyhedra`

当前已接入主链的 graph family 包括：

- `ring`
- `grid`
- `nest`
- `stack`
- `shell`
- `boolean`

结论：

- 当前 geometry 已经超出最早的三类基本体阶段
- 但还没有达到“大多数 Geant4 工程几何都能稳定覆盖”的程度

---

## 5. 提交控制：Arbiter + Gate

这是当前系统最核心的稳定性设计。

### 5.1 Arbiter

Arbiter 负责：

- 候选更新过滤
- target path 对齐
- 冲突裁决
- 锁冲突处理
- overwrite 预览

相关文件：

- `core/orchestrator/candidate_preprocess.py`
- `core/orchestrator/session_manager.py`
- `core/orchestrator/types.py`

### 5.2 Constraint Ledger

已确认内容会进入约束账本，用于：

- 防止未授权覆盖
- 支持 confirm / reject
- 保留审计轨迹

### 5.3 Validator Gate

相关文件：

- `core/validation/validator_gate.py`
- `core/validation/geometry_registry.py`

Gate 负责检查：

- 最小闭环完整性
- geometry family 所需字段
- graph program 一致性
- 材料与 volume 绑定
- source / physics / output 基本可用性

当前主链的正确性，主要依赖这一层而不是依赖 LLM 自觉。

---

## 6. 对话层设计

### 6.1 动作层

当前对话动作包括：

- `ASK_CLARIFICATION`
- `SUMMARIZE_PROGRESS`
- `CONFIRM_OVERWRITE`
- `REJECT_OVERWRITE`
- `FINALIZE`
- `EXPLAIN_CHOICE`

相关文件：

- `core/dialogue/types.py`
- `core/dialogue/state.py`
- `core/dialogue/renderer.py`
- `core/dialogue/action_templates.py`
- `planner/agent.py`

### 6.2 当前策略

当前采用的是：

- 动作级模板
- LLM 轻度自然化

而不是：

- 场景级模板
- 整段脚本式对话模板

这是当前最稳的折中，因为：

- 约束足够强
- 可以限制内部字段泄漏
- 仍保留一定自然语言表现力

### 6.3 当前已隐藏的内部字段

用户层摘要现在默认隐藏：

- `geometry.graph_program`
- `geometry.chosen_skeleton`
- `geometry.root_name`
- `physics.backup_physics_list`
- `physics.covered_processes`
- 各类 `selection_source`
- 各类 `selection_reasons`

---

## 7. 当前验证证据

### 7.1 已通过的 live 多轮回归

当前已通过的核心集合：

- `docs/eval_casebank_multiturn_live_v2_12.json`

最近一次 live 结果：

- JSON: `docs/casebank_regression_2026-03-07_145107.json`
- EN PDF: `docs/casebank_regression_report_en_2026-03-07_145107.pdf`
- ZH PDF: `docs/casebank_regression_report_zh_2026-03-07_145107.pdf`

关键指标：

- `pass_rate = 1.0000`
- `initial_alignment_rate = 1.0000`
- `final_alignment_rate = 1.0000`
- `missing_reduction_rate = 1.0000`
- `confirm_apply_success_rate = 1.0000`
- `rollback_after_confirm_rate = 0.0000`
- `internal_leak_turn_rate = 0.0000`
- `stale_confirm_case_rate = 0.0000`

### 7.2 新增扩展 live casebank

为继续扩覆盖，我已经新增：

- `docs/eval_casebank_multiturn_live_v3_24.json`

这个集合的特点是：

- 在原有 12 个 case 基础上扩到 24 个
- 增加了更多 geometry-heavy operator-graph 场景：
  - `ring`
  - `grid`
  - `stack`
  - `nest`
  - `shell`
  - `boolean`

它更适合作为下一阶段 live 压测的主集合。

---

## 8. 当前边界

当前系统仍有以下边界：

1. 还不是完整 Geant4 运行工程生成器
2. 复杂几何覆盖仍不足
3. 更复杂 boolean 与多级装配仍未完全打通
4. RAG 仍未正式接入主链
5. BERT 当前主要是 prior，不是强分类中心
6. 评测规模仍然偏小，尚不足以支持公开发布声明

---

## 9. 后续建议

当前后续工作应按下面顺序推进：

### P1

1. 用 `docs/eval_casebank_multiturn_live_v3_24.json` 跑下一轮 live 回归
2. 针对 geometry-heavy 场景补失败用例
3. 继续扩 family-aware 缺参追问

### P2

1. 扩真实用户测试样本
2. 继续优化用户层自然度
3. 根据回归结果决定是否重训 BERT prior

### 当前不建议做的事

- 不建议再推翻主架构
- 不建议回到结构分类中心化
- 不建议引入 per-scenario template

---

## 10. 总结

当前版本最关键的判断是：

1. **架构已经站住。**
2. **接下来主要是扩覆盖，而不是再重构。**

如果没有新的 P0 问题出现，后续工作应以：

- 大一点的 live casebank
- 更复杂的几何回归
- 更真实的用户测试

为主线继续推进。
