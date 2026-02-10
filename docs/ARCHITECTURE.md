# Architecture Redesign Draft

This document proposes a layered architecture that upgrades **BERT_Lab** from a geometry-only helper into a **multi-domain NLU core**. The goal is to avoid patchwork logic by making each layer’s responsibilities explicit and stable.

**Design goals**
1. BERT_Lab becomes the **Semantic Core**, not just a geometry parser.
2. LLM is used for **planning and dialogue**, not for low-level parsing.
3. Builders are deterministic: given a semantic frame, they generate configs.
4. Verifiers are conservative: they check feasibility and report gaps.

## Layers (4+1)
1. **NLU Layer (BERT_Lab)**
   - Tasks: structure classification, parameter extraction, entity spotting (materials, particles, physics list, output).
   - Output: `SemanticFrame` (single unified structure).

2. **Planner Layer (LLM + rules)**
   - Decides which domain to ask about next.
   - Generates human-friendly clarification questions.
   - Does NOT do geometry math.

3. **Builder Layer (Geometry + Config)**
   - Converts `SemanticFrame` into DSL/config.
   - No guessing, only deterministic assembly.

4. **Verifier Layer (Feasibility + Constraints)**
   - Checks DSL/config for feasibility.
   - Emits structured errors + suggestions.

5. **UI Layer**
   - Maintains session state.
   - Multi-turn dialogue with user.

## Data Flow
User text → **NLU** → `SemanticFrame` → **Planner** → ask user → user reply → **NLU** → ...  
When complete: **Builder** → config/DSL → **Verifier** → final output.

## SemanticFrame (single contract)
`core/semantic_frame.py` is the canonical structure. Every layer reads/writes this.

Example (minimal):
```json
{
  "geometry": {"structure": "single_box", "params": {"module_x": 1000, "module_y": 1000, "module_z": 1000}},
  "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {}},
  "source": {"type": "point", "particle": "gamma"},
  "physics": {"physics_list": "FTFP_BERT"},
  "output": {"format": "root"},
  "environment": {"temperature": null, "pressure": null},
  "notes": []
}
```

## Directory Mapping (after adjustment)
- `nlu/bert_lab/` → NLU layer (BERT-based parsing)
- `planner/flows/` → LLM-driven planning and question generation
- `builder/geometry/` → Geometry DSL + feasibility
- `knowledge/` → Authoritative lists and constraints
- `ui/web/` → Web UI + session state
- `core/` → shared schema + semantic frame

## Immediate Refactor Tasks (non-breaking)
1. Expand BERT_Lab label space to include **materials/particles/physics/output**.
2. Add a thin adapter that converts BERT output into `SemanticFrame`.
3. Move all UI logic to consume/emit `SemanticFrame`, not raw params.
4. Keep LLM as **planner/questioner**, never a geometry calculator.

---

# 架构改造设计稿（中文）

本设计将 **BERT_Lab** 升级为“多域语义核心”，解决目前“几何补丁式逻辑”的问题。目标是让每一层职责明确、可扩展、可测试。

**设计目标**
1. BERT_Lab 变成**语义核心**，不止是几何解析。
2. LLM 只负责**规划和对话**，不做底层几何计算。
3. Builder 必须确定性输出（不猜测）。
4. Verifier 只做保守验证与提示。

## 分层（4+1）
1. **NLU层（BERT_Lab）**
   - 结构分类、参数抽取、材料/粒子/物理过程/输出格式识别
   - 输出统一 `SemanticFrame`

2. **Planner层（LLM + 规则）**
   - 决定接下来要问什么
   - 生成用户友好的追问
   - 不参与几何计算

3. **Builder层（几何 + 配置构建）**
   - 将 `SemanticFrame` 转为 DSL / config
   - 不猜测、不补脑

4. **Verifier层（可行性 + 约束）**
   - 保守判定
   - 输出错误与建议

5. **UI层**
   - 维护对话状态
   - 多轮交互

## 数据流
用户输入 → **NLU** → `SemanticFrame` → **Planner** → 追问 → 用户回答 → **NLU** → ...  
补齐后：**Builder** → config/DSL → **Verifier** → 输出结果。

## SemanticFrame（统一契约）
`core/semantic_frame.py` 为所有层共享结构。

## 目录映射（已调整）
- `nlu/bert_lab/` → NLU 层
- `planner/flows/` → 规划与追问
- `builder/geometry/` → 几何 DSL + 可行性
- `knowledge/` → 约束与知识库
- `ui/web/` → Web UI
- `core/` → 共享 schema + 语义帧

## 下一步（不破坏原功能）
1. 扩展 BERT_Lab 标签空间（材料/粒子/物理过程/输出格式）
2. 增加 BERT→SemanticFrame 适配器
3. UI 全部基于 `SemanticFrame` 流转
4. LLM 只做 Planner，不碰几何计算
