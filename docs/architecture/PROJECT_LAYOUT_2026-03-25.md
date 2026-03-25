# Project Layout 2026-03-25

## Active runtime paths

- `core/`: domain logic, orchestration, validation, contracts
- `nlu/`: LLM/BERT extraction and normalization
- `mcp/`: runtime-facing tool boundaries
- `runtime/`: local Geant4 app and runtime-side executables
- `ui/web/`: active browser UI renderer and HTTP handlers
- `ui/launch/`: active UI launch/runtime entry points

## Compatibility paths

- `ui/desktop/`: compatibility wrappers kept for older launch scripts/import paths
- `legacy/`: archived experiments, reports, old tools, retired desktop shells

## Notes

- The browser-based UI path is the current primary local entrypoint.
- `ui/desktop/` no longer contains the active desktop-shell implementation.
- Geometry refactoring should target `core/geometry/` rather than `builder/geometry/`.

