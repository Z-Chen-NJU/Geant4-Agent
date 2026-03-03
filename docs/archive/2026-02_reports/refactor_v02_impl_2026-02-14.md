# V0.2 重构实现说明（已落地）

## 范围
- 已按 `v0.1/v0.2` 主线落地：单一真值源、约束账本、候选更新池、仲裁器、三层校验门、审计轨迹。
- `LLM/BERT` 已降级为“只产提案，不直接落盘”。

## 新增模块
- `core/orchestrator/types.py`
- `core/orchestrator/path_ops.py`
- `core/orchestrator/phase_machine.py`
- `core/orchestrator/constraint_ledger.py`
- `core/orchestrator/intent_guard.py`
- `core/orchestrator/arbiter.py`
- `core/orchestrator/session_manager.py`
- `core/validation/error_codes.py`
- `core/validation/minimal_schema.py`
- `core/validation/geometry_registry.py`
- `core/validation/validator_gate.py`
- `core/audit/audit_log.py`
- `nlu/llm/normalizer.py`
- `nlu/llm/recommender.py`
- `nlu/bert/extractor.py`

## Web 接入变更
- `ui/web/server.py`
  - `step()` 默认走 `strict_mode=true` 的新 Orchestrator 流程。
  - `/api/reset` 同步重置新会话管理器。
  - 新增 `/api/audit` 用于导出会话审计轨迹。
- `ui/web/app.js`
  - 请求 payload 默认附带 `strict_mode: true`。

## 已实现的硬约束
1. phase 只由 Orchestrator 推进（`phase_machine.py`）。
2. 锁字段覆盖检查（`intent_guard.py` + `constraint_ledger.py`）。
3. 候选仲裁可复现（优先级/置信度/producer_rank/turn_id）。
4. `single_box` 参数白名单清洗（`geometry_registry.py`）。
5. `volume_material_map` 与几何 root 绑定检查。
6. Layer C 最小闭环 required 路径统一（`minimal_schema.py`）。
7. 每轮审计：accepted/rejected/diff/violations（`audit_log.py`）。

## 当前已验证行为
- 1m×1m×1m 单盒体不会在后续“物理列表推荐回合”被改写为其他结构。
- `pitch/tilt` 等 single_box 无关字段会被作用域清洗并记录 `E_SCOPE_LEAK` warning。
- 纯 gamma + no hadron 请求可由 LLM recommender 写入 physics 选择，并保留理由与覆盖过程字段。

## 注意
- 该版本是重构落地的第一版，仍保留旧 `step` 代码路径（`strict_mode=false`）用于回退调试。
- 评测脚本尚未全面迁移到新 Orchestrator（后续可统一到 `/api/step(strict_mode=true)`）。
