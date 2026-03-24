$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$venvPython = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
  throw "Missing virtual environment python: $venvPython"
}

$env:G4_DESKTOP_PYTHON = $venvPython

Set-Location $root
& $venvPython -m ui.browser_shell
