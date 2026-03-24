# Chromium UI Migration Design

## Goal

Move the current local web console into a Chromium desktop shell without forcing a full frontend rewrite.

The desktop shell should become the main user-facing entrypoint once local Geant4 runtime control and artifact display are added.

## Recommended runtime shape

User
-> Chromium desktop shell
-> local Python bridge
-> orchestrator / MCP / Geant4 adapter
-> local Geant4 wrapper
-> result artifacts
-> desktop UI

## Stage 1

Stage 1 is intentionally conservative:

- keep `ui/web/` as the renderer payload
- replace "open in browser" with "open in Chromium shell"
- start the existing Python runtime through a desktop-controlled bridge

This gives the project:

- desktop lifecycle control
- local process ownership
- cleaner future integration with Geant4
- no immediate renderer rewrite

## Stage 1 modules

- `ui/desktop/main.js`
  - Electron main process
  - spawns Python bridge
  - waits for runtime readiness
  - opens the Chromium window

- `ui/desktop/preload.js`
  - controlled bridge for renderer metadata
  - keeps Node disabled in the renderer

- `ui/desktop/runtime_bridge.py`
  - starts the current local HTTP interface
  - reuses `ui.web.server.Handler`

## Why not keep browser-only Web UI

Browser-only mode is weaker for the intended Geant4 workflow:

- local process control is awkward
- artifact access is indirect
- local file and runtime lifecycle handling are not first-class
- desktop integration is limited

## Why not switch directly to TUI

TUI remains useful for development and debugging, but it is not a strong primary shell for:

- visualization snapshots
- runtime health panels
- multi-pane dialogue plus config plus logs
- future interactive result inspection

## Recommended next steps

1. Add desktop-facing APIs for:
   - runtime health
   - Geant4 run status
   - latest artifact paths
   - log tails

2. Add a simulation panel to the renderer:
   - runtime phase
   - run button
   - latest Geant4 log tail
   - latest snapshot path / preview

3. Move `ui/web/app.js` toward modular renderer code once the desktop shell becomes the default entrypoint.
