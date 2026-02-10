# Knowledge Layer (Stage 1)

This module provides **structured, verifiable knowledge** for materials and
environment parameters. JSON is the source of truth; RAG is a helper for
explanations and disambiguation.

## Contents

- `schema/`: JSON schema for materials and environment.
- `data/`: Material lists and environment defaults/constraints.
- `validate.py`: Validation helpers.
- `cli.py`: Validate a JSON payload.
- `tools/`: Data fetchers (official Geant4 sources).
- `rag/`: Placeholder for future retrieval index.

## Data Sources (Stage 1)

- Geant4 Application Developers Guide: material definitions and concepts.
- Geant4 NIST material name list (official material names).

See `data/materials_geant4_nist.json` for the fetched list and metadata.

## Project Lists (Stage 1)

- `data/physics_lists.json`: common Geant4 physics lists (curated).
- `data/particles.json`: common particle names (curated).
- `data/output_formats.json`: common output formats (curated).

Notes:
- `data/physics_lists.json` is fetched from the official reference physics list index.
- `data/particles.json` is fetched from the official Geant4 particle list pages.
- `data/output_formats.json` remains project-defined (not an official Geant4 list).
