# Geant4-Agent 阶段更新汇总（中文）

## 1. 本轮目标
- 提升「自然语言 -> 归一化 -> 参数抽取 -> 几何可行性 -> 多轮补参」链路在接入 Ollama 后的稳定性。
- 解决此前 workflow 中的三个关键问题：
  - 归一化输出键名不统一（如 `num_elements` / `element_size` 无法直接进入几何参数链路）。
  - 材料名称口语表达与 Geant4 NIST 名称不一致（如 `copper` 未映射到 `G4_Cu`）。
  - 交互结果中出现 `<think>` 噪声，影响 UI 可读性。

## 2. 关键改动
- 归一化 Prompt 约束升级（强制 canonical keys，禁止别名键，缺失几何时强制 `unresolved`）。
  - 文件：`nlu/bert_lab/llm_bridge.py`
- 参数后处理新增 alias -> canonical 映射。
  - 示例：`num_elements -> n`，`element_size -> module_x/module_y/module_z`
  - 文件：`nlu/bert_lab/postprocess.py`
- 材料别名映射增强（英文常见词 -> Geant4 NIST 材料名）。
  - 示例：`copper -> G4_Cu`，`silicon -> G4_Si`
  - 文件：`nlu/bert_lab/semantic.py`
- Source 文本解析增强（支持 `at (x,y,z) to (dx,dy,dz)`）。
  - 文件：`ui/web/server.py`
- 自动补全 `materials.volume_material_map`（已有 geometry + material 时自动映射到 `target`）。
  - 文件：`ui/web/server.py`
- 追问文本清洗（移除 `<think>...</think>`）。
  - 文件：`planner/agent.py`

## 3. 验证结果（接入 Ollama）
- 缩小版完整 workflow（自然语言 + Ollama + 多轮）：
  - 结果文件：`nlu/bert_lab/data/eval/workflow_e2e_lite_report_ollama_v2.json`
  - 指标：`workflow_acc = 1.0`（3/3）
- 3 类回归（含归一化链路）：
  - 结果文件：`nlu/bert_lab/data/eval/regression_3class_results_ollama_v2.json`
  - 指标：`structure_acc = 1.0`，`feasible_acc = 1.0`
- 对应展示报告：
  - `docs/workflow_e2e_lite_report_2026-02-13_ollama_v2.md`
  - `docs/regression_3class_report_2026-02-13_ollama_v2.md`

## 4. 你本地如何复现
1. 启动/确认 Ollama 可用（并确保模型已拉取）。
2. 在项目根目录执行：

```powershell
$env:OLLAMA_CONFIG_PATH="nlu/bert_lab/configs/ollama_config_expert_fast.json"
.\.venv\Scripts\python -m nlu.bert_lab.run_workflow_e2e_lite --autofix --lang en --out_json nlu/bert_lab/data/eval/workflow_e2e_lite_report_ollama_v2.json --out_md docs/workflow_e2e_lite_report_2026-02-13_ollama_v2.md
.\.venv\Scripts\python -m nlu.bert_lab.run_regression_3class --autofix --normalize_input --out_json nlu/bert_lab/data/eval/regression_3class_results_ollama_v2.json --out_md docs/regression_3class_report_2026-02-13_ollama_v2.md
```

## 5. UI 入口是否变化
- 没变，入口和以前一致。
- 启动命令：

```powershell
.\.venv\Scripts\python ui/web/server.py
```

- 浏览器访问：`http://127.0.0.1:8088`
- 新增：可在 UI 的 `LLM Config` 下拉框直接切换模型配置（后端实时切换）。
- 默认配置已切到 14B：`nlu/bert_lab/configs/ollama_config.json` -> `qwen3:14b`

## 6. 当前状态与下一步
- 当前状态：已经达到可演示的端到端基础可用版本（含 Ollama 工作流）。
- 下一步建议：
  - 扩展 workflow case 数（>20）并分层统计（ideal / realistic / hard）。
  - 把评测报告统一整理为 UTF-8 中文模板，避免历史文件编码混杂。
  - 继续补几何算子覆盖面，并同步扩展参数映射词表。
