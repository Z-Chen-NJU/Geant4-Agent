# Geant4-Agent 使用方法与本地部署说明

## 1. 适用范围

这份说明面向两类场景：

1. 在本机启动 Web UI，做多轮 first-pass 配置生成
2. 在另一台 Windows 机器上复现当前项目

当前版本适合：

- 本地验证
- 内部测试
- 受控真人试用

当前版本不适合：

- 直接作为完整 Geant4 工程生成器发布
- 不受控公开测试

---

## 2. 推荐环境

### 2.1 操作系统

推荐：

- Windows 10 / 11

当前项目的既有使用方式与脚本路径明显是 Windows-first。

### 2.2 Python

推荐：

- Python `3.10+`

当前本地环境实际运行在 Python 3.12。

### 2.3 硬件

- 只做推理与 Web UI：CPU 可运行
- 做本地训练或高频推理：建议 NVIDIA GPU

---

## 3. 获取代码

假设项目目录为：

```powershell
F:\geant4agent
```

后续命令默认都在仓库根目录执行。

---

## 4. 创建虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

如果 PowerShell 限制脚本执行，可先运行：

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

---

## 5. 安装依赖

当前仓库没有统一锁定的 `requirements.txt`，建议安装最小运行依赖。

### 5.1 CPU 安装

```powershell
python -m pip install torch transformers safetensors
```

### 5.2 CUDA GPU 安装（示例：CUDA 12.1）

```powershell
python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
python -m pip install transformers safetensors
```

如果你的 CUDA 版本不同，应改成匹配的 PyTorch wheel 源。

### 5.3 当前核心依赖

运行时主要依赖：

- `torch`
- `transformers`
- `safetensors`

Web UI 本身基于 Python 标准库 `http.server`，不依赖 Flask/FastAPI。

---

## 6. 准备 LLM 配置

配置目录：

- `nlu/bert_lab/configs/`

当前可用示例：

- `ollama_config.json`
- `ollama_config_fast.json`
- `ollama_config_expert_fast.json`
- `openai_compatible_config.example.json`
- `deepseek_api_config.example.json`

### 6.1 使用 Ollama

编辑：

- `nlu/bert_lab/configs/ollama_config.json`

确保以下字段正确：

- `provider`
- `base_url`
- `model`

### 6.2 使用 OpenAI 兼容接口 / DeepSeek

可新建一个本地私有配置，例如：

- `nlu/bert_lab/configs/deepseek_api.local.json`

示例：

```json
{
  "provider": "deepseek",
  "base_url": "https://api.deepseek.com",
  "chat_path": "/chat/completions",
  "model": "deepseek-chat",
  "timeout_s": 120,
  "api_key": "<YOUR_API_KEY>",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

不要把私钥配置提交到版本库。

---

## 7. 准备本地模型

运行时会自动检查：

- structure 模型目录
- `ner` 模型目录

默认检查逻辑在：

- `nlu/runtime_components/model_preflight.py`

### 7.1 默认 structure 模型候选目录

系统会优先寻找以下目录之一：

- `nlu/bert_lab/models/structure_controlled_v4c_e1`
- `nlu/bert_lab/models/structure_controlled_v3_e1`
- `nlu/bert_lab/models/structure_controlled_smoke`
- `nlu/bert_lab/models/structure_opt_v3`
- `nlu/bert_lab/models/structure_opt_v2`
- `nlu/bert_lab/models/structure`

### 7.2 默认 NER 模型目录

- `nlu/bert_lab/models/ner`

### 7.3 模型目录最低要求

模型目录至少应包含：

- `config.json`
- tokenizer 资产之一：
  - `tokenizer.json`
  - `vocab.txt`
  - `vocab.json + merges.txt`
  - sentencepiece 文件

### 7.4 重要说明

仓库默认不附带训练好的模型权重。

如果你在另一台机器部署，需要：

- 把本地训练好的模型目录复制过去
- 或在新机器重新训练

---

## 8. 启动 Web UI

```powershell
python ui\web\server.py
```

启动后访问：

- `http://127.0.0.1:8088`

启动日志会打印：

- 当前 provider
- 当前 model
- 当前 base URL
- model preflight 结果

如果 preflight 显示：

- `structure_ok=false`
- 或 `ner_ok=false`

说明模型目录尚未准备好。

---

## 9. 本地使用流程

推荐使用流程：

1. 启动 Web UI
2. 确认当前 LLM config 指向正确 provider
3. 输入自然语言需求
4. 跟随系统进行多轮补参
5. 查看输出 JSON 与用户层摘要

当前系统已经支持：

- fuzzy 首轮保守处理
- overwrite 确认 / 拒绝
- graph family 的 family-aware 缺参追问

---

## 10. 仅运行 geometry 理论部分

如果你只想运行 geometry DSL 与理论验证，不需要启动 UI。

```powershell
python -m builder.geometry.cli run_all --outdir builder/geometry/out --n_samples 200 --n_param_sets 100 --seed 7 --dataset builder/geometry/examples/coverage.csv
```

预期输出：

- `builder/geometry/out/coverage_summary.json`
- `builder/geometry/out/coverage_checked.jsonl`
- `builder/geometry/out/feasibility_summary.json`
- `builder/geometry/out/ambiguity_summary.json`

这部分不依赖 Geant4 运行时，只做理论层检查。

---

## 11. 运行回归测试

### 11.1 当前已验证的 live 集合

```powershell
python scripts/run_casebank_regression.py --dataset docs/eval_casebank_multiturn_live_v2_12.json --config nlu/bert_lab/configs/deepseek_api.local.json --outdir docs --baseline docs/casebank_baseline.json --min_confidence 0.6
```

最近一次结果：

- `pass_rate = 1.0000`
- `internal_leak_turn_rate = 0.0000`

输出内容包括：

- JSON 报告
- 中英文 PDF 报告
- LaTeX 源文件

### 11.2 检查 casebank 分布

```powershell
python scripts/verify_eval_casebank.py --dataset docs/eval_casebank_multiturn_live_v3_24.json
```

这一步只检查数据集分布，不调用 LLM。

---

## 12. 本地训练 BERT

### 12.1 构建 structure v2 数据集

```powershell
python scripts/build_structure_v2_dataset.py --base nlu/bert_lab/data/controlled_structure.jsonl --extra nlu/bert_lab/data/controlled_multitask.jsonl --out nlu/bert_lab/data/controlled_structure_v2.jsonl --keep_original
```

### 12.2 训练 structure 模型

```powershell
python scripts/train_structure_v2.py --config nlu/bert_lab/configs/structure_train_v2.json --outdir nlu/bert_lab/models/structure_controlled_v5_e2 --device cuda
```

训练输出放到：

- `nlu/bert_lab/models/structure_controlled_v5_e2`

之后 runtime preflight 会自动发现它。

---

## 13. 在另一台 Windows 机器部署

推荐顺序：

1. 复制代码仓库
2. 创建 `.venv`
3. 安装 `torch + transformers + safetensors`
4. 复制本地训练好的模型到 `nlu/bert_lab/models/`
5. 准备 LLM 配置文件
6. 启动 `python ui\\web\\server.py`
7. 打开浏览器访问 `http://127.0.0.1:8088`

### 如果 LLM 在远端

例如：

- 远端机器运行 Ollama
- 本机通过 SSH 转发到 `11434`

只需要把配置文件中的 `base_url` 改到本机转发地址，例如：

- `http://127.0.0.1:11434`

项目本身不要求模型与 UI 跑在同一台机器。

---

## 14. 常见问题

### 14.1 UI 能打开，但对话不工作

优先检查：

1. LLM 配置是否正确
2. API key 是否有效
3. model preflight 是否通过
4. structure 与 NER 模型目录是否都存在

### 14.2 回复很机械

这通常不是部署故障，而是：

- 当前动作级模板在起保护作用
- 或 LLM 自然化被拒绝后回退到安全模板

### 14.3 配置能理解，但某些字段不提交

当前主链已经修复已知 P0 提交问题。若仍出现，优先检查：

- 是否是 fuzzy 首轮
- 是否被 lock 拦截
- 是否被 explicit target filter 丢弃
- 是否被 Gate 拒绝

### 14.4 为什么当前不直接输出完整 Geant4 工程

因为当前优先级是：

- 先做对话闭环
- 先做配置正确性
- 先保证可解释和可追问

完整工程生成仍在后续阶段。

---

## 15. 部署建议

如果你的目标是：

- 本地验证
- 内部测试
- 受控试用

当前版本已经可以使用。

如果你的目标是：

- 面向外部用户直接开放
- 对复杂几何做高覆盖承诺
- 直接输出完整 Geant4 工程

当前版本还不够，需要继续扩大 live casebank 并补复杂几何回归。
