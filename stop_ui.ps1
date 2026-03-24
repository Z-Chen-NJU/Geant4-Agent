$ErrorActionPreference = "SilentlyContinue"

$ports = @(8088, 8099)
$pids = @()

foreach ($port in $ports) {
  $lines = netstat -ano -p TCP | Select-String "127.0.0.1:$port"
  foreach ($line in $lines) {
    $text = ($line.ToString() -replace "\s+", " ").Trim()
    $parts = $text.Split(" ")
    if ($parts.Length -ge 5) {
      $pid = $parts[-1]
      if ($pid -match "^\d+$" -and $pids -notcontains $pid) {
        $pids += $pid
      }
    }
  }
}

if (-not $pids) {
  Write-Output "No UI bridge is listening on 127.0.0.1:8088 or 127.0.0.1:8099"
  exit 0
}

foreach ($pid in $pids) {
  taskkill /PID $pid /F | Out-Null
  Write-Output "Stopped UI bridge process $pid"
}
