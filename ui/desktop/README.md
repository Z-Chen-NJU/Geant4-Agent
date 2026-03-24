# Geant4-Agent UI Launchers

The current recommended UI path is the local web app served by Python and opened in the system browser.

Current design:

- `ui.browser_shell`: primary launcher for the local web UI
- `start_ui.ps1`: top-level startup script
- `start_desktop.ps1`: compatibility launcher that now forwards to the browser-based UI path
- `desktop_shell.py`: older `pywebview` experiment kept in-tree, no longer the recommended path
- `main.js`: Electron experiment entry kept in-tree, but currently blocked by an upstream Windows module-loading issue
- `runtime_bridge.py`: starts the existing Python HTTP runtime locally
- `package.json`: desktop shell package metadata

The renderer remains the same `ui/web/` frontend.

## Intended startup flow

1. `python -m ui.browser_shell` starts.
2. It spawns `python -m ui.desktop.runtime_bridge` if port `8088` is not already in use.
3. The Python bridge serves the current `ui/web/` frontend and APIs.
4. The launcher opens `http://127.0.0.1:8088` in the system browser.

## Local test path

Preferred:

```powershell
.\start_ui.ps1
```

Manual:

```powershell
.\.venv\Scripts\python -m ui.browser_shell
```

Bridge-only:

```powershell
.\.venv\Scripts\python -m ui.desktop.runtime_bridge --host 127.0.0.1 --port 8088
```

## What should work now

- the launcher starts the Python bridge automatically
- the multi-turn dialogue workspace loads in the browser
- Geant4 runtime panel appears
- `Sync Config` pushes current config into the local Geant4 adapter
- `Initialize` transitions runtime state to initialized
- `Run 1 Event` and `Run 10 Events` invoke the local wrapper and show the latest log tail
- `Open Viewer` launches the native Geant4 visual window separately

## Current recommendation

Use `start_ui.ps1` for actual testing.

Electron and `pywebview` remain in the tree only as experiments. The current reliable local entry is the browser-based UI.

## Why this layout

- Keeps the current frontend assets usable.
- Avoids a premature rewrite of the UI layer.
- Gives the desktop shell control over lifecycle, local process startup, and future Geant4 integration.

## Next migration steps

1. Add explicit desktop-only APIs for runtime state, Geant4 artifacts, and local file actions.
2. Refactor `ui/web/app.js` into renderer modules.
3. Add a dedicated simulation panel for Geant4 run status, logs, and snapshots.
