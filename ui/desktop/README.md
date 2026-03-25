`ui/desktop/` is now a compatibility shell.

Active launch/runtime entry points live under `ui/launch/`.

What remains here:
- `runtime_bridge.py`: compatibility import path for older launchers
- `start_desktop.ps1`: compatibility launcher that forwards to the browser UI path

Historical Electron and desktop-shell experiments were moved to:
- `legacy/ui_desktop/`
