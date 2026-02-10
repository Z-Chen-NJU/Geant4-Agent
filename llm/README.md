# LLM Layer

This layer hosts prompts and flow scripts that talk to Ollama and produce
structured outputs constrained by JSON schema.

## Minimal Config Flow

```powershell
python llm/flows/min_config_flow.py --text "Make a small detector with a box and silicon inside."
```

The output includes:
- `raw`: raw LLM response
- `config`: parsed JSON if valid

---

# LLM 层

该层包含 Ollama prompt 与流程脚本，用于在 JSON schema 约束下生成结构化输出。

## 最小配置流程

```powershell
python llm/flows/min_config_flow.py --text "Make a small detector with a box and silicon inside."
```

输出包括：
- `raw`：LLM 原始回复
- `config`：解析后的 JSON
