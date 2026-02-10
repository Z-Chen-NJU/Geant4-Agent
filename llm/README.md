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
