$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$serverScript = Join-Path $root "ui\run_ui_server.py"
$port = 8099
$url = "http://127.0.0.1:$port"

if (-not (Test-Path $venvPython)) {
  throw "Missing virtual environment python: $venvPython"
}

if (-not (Test-Path $serverScript)) {
  throw "Missing UI server script: $serverScript"
}

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "stop_ui.ps1") | Out-Null

$browserJob = Start-Job -ScriptBlock {
  param($targetUrl)
  Start-Sleep -Seconds 2
  Start-Process $targetUrl | Out-Null
} -ArgumentList $url

Write-Output "Starting Geant4-Agent UI at $url"
Set-Location $root
& $venvPython $serverScript --host 127.0.0.1 --port $port
