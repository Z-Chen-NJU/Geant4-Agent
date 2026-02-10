# Geant4-Agent

A Geant4-oriented geometry assembly prototype: DSL + feasibility checker, plus a BERT lab for
structure/parameter extraction.

## Repository Layout

This repo is split into four layers:

- `geometry/`: DSL + feasibility checker + experiments (Geant4-style assemblies)
- `bert_lab/`: A small, isolated starting point for BERT-based parameter extraction
- `knowledge/`: Materials/environment knowledge (JSON schema + validation)
- `llm/`: Ollama-driven prompt flows and JSON-schema constrained generation

## Architecture Overview

- **Geometry core** (`geometry/`): DSL + analytical feasibility checks. Produces errors, warnings, and suggestions.
- **Language core** (`bert_lab/`): Structure classification + parameter extraction + postprocess.
- **Knowledge layer** (`knowledge/`): JSON schema, validated lists (materials, particles, physics lists), and validation.
- **LLM layer** (`llm/`): Prompt flows and schema-constrained outputs via Ollama.

## Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Geometry Quick Start

```powershell
python -m geometry.cli run_all --outdir geometry/out --n_samples 200 --n_param_sets 100 --seed 7 --dataset geometry/examples/coverage.csv
```

Expected outputs:
- `geometry/out/coverage_summary.json`
- `geometry/out/coverage_checked.jsonl`
- `geometry/out/feasibility_summary.json`
- `geometry/out/ambiguity_summary.json`

## BERT Lab Quick Start

```powershell
python bert_lab/bert_lab_data.py --out bert_lab/bert_lab_samples.jsonl --n 200 --seed 7
```

## Knowledge Quick Start

Fetch Geant4 NIST material names (official list):

```powershell
python knowledge\\tools\\fetch_geant4_materials.py
```

## Current Limitations

- **No full Geant4 runtime config**: schema exists, but no full generator of G4 macro or C++ config.
- **Physics lists are reference-only**: fetched from official “reference” list, not a complete superset.
- **Output formats are project-defined**: not an official Geant4 list.
- **RAG not implemented**: `knowledge/rag/` is a placeholder; no retrieval index yet.
- **Material ↔ volume mapping is manual**: needs explicit `volume_names` to validate mappings.
- **BERT data is synthetic-heavy**: real-world robustness still unverified.
