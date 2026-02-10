# Geant4-Agent

A Geant4-oriented geometry assembly prototype: DSL + feasibility checker, plus a BERT lab for
structure/parameter extraction.

面向 Geant4 的几何装配原型：包含 DSL 与可行性检查，以及用于结构/参数抽取的 BERT Lab。

## Repository Layout / 仓库结构

This repo is split into four layers:

本仓库分为四层：

- `geometry/`: DSL + feasibility checker + experiments (Geant4-style assemblies)  
  DSL + 理论可行性检查 + 实验
- `bert_lab/`: A small, isolated starting point for BERT-based parameter extraction  
  BERT 结构/参数抽取实验区
- `knowledge/`: Materials/environment knowledge (JSON schema + validation)  
  材料/环境知识层（JSON schema + 校验）
- `llm/`: Ollama-driven prompt flows and JSON-schema constrained generation  
  LLM 层（Ollama 驱动的 prompt 流程与 schema 约束）

## Architecture Overview / 架构概览

- **Geometry core** (`geometry/`): DSL + analytical feasibility checks. Produces errors, warnings, and suggestions.  
  几何核心：DSL + 解析可行性判定，输出错误/警告/建议。
- **Language core** (`bert_lab/`): Structure classification + parameter extraction + postprocess.  
  语言核心：结构分类 + 参数抽取 + 后处理。
- **Knowledge layer** (`knowledge/`): JSON schema, validated lists, and validation.  
  知识层：JSON schema、可溯源列表与校验。
- **LLM layer** (`llm/`): Prompt flows and schema-constrained outputs via Ollama.  
  LLM 层：Ollama prompt 流程与 schema 约束输出。

## Virtual Environment / 虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Geometry Quick Start / 几何快速开始

```powershell
python -m geometry.cli run_all --outdir geometry/out --n_samples 200 --n_param_sets 100 --seed 7 --dataset geometry/examples/coverage.csv
```

Expected outputs / 预期输出：
- `geometry/out/coverage_summary.json`
- `geometry/out/coverage_checked.jsonl`
- `geometry/out/feasibility_summary.json`
- `geometry/out/ambiguity_summary.json`

## BERT Lab Quick Start / BERT 快速开始

```powershell
python bert_lab/bert_lab_data.py --out bert_lab/bert_lab_samples.jsonl --n 200 --seed 7
```

## Knowledge Quick Start / 知识层快速开始

Fetch Geant4 NIST material names (official list) / 抓取官方材料名单：

```powershell
python knowledge\\tools\\fetch_geant4_materials.py
```

## Current Limitations / 当前限制

- **No full Geant4 runtime config**: schema exists, but no full generator of G4 macro or C++ config.  
  尚未生成完整可运行的 Geant4 宏或 C++ 配置，仅有 schema。
- **Physics lists are reference-only**: fetched from official “reference” list, not a complete superset.  
  物理列表仅覆盖官方 reference 列表，并非完整集合。
- **Output formats are project-defined**: not an official Geant4 list.  
  输出格式为项目定义，非官方 Geant4 列表。
- **RAG not implemented**: `knowledge/rag/` is a placeholder; no retrieval index yet.  
  RAG 尚未实现，仅留占位目录。
- **Material ↔ volume mapping is manual**: needs explicit `volume_names` to validate mappings.  
  材料与体积映射需手工指定 `volume_names` 才能校验。
- **BERT data is synthetic-heavy**: real-world robustness still unverified.  
  BERT 训练数据以合成为主，真实输入鲁棒性待验证。
