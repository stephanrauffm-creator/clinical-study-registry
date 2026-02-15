param(
    [int]$KeepDays = 14,
    [string]$ProjectRoot = $(Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

if ($KeepDays -lt 1) {
    throw "KeepDays must be >= 1."
}

$dbPath = Join-Path $ProjectRoot "db.sqlite3"
if (-not (Test-Path -LiteralPath $dbPath)) {
    throw "Database file not found: $dbPath"
}

$backupRoot = Join-Path $ProjectRoot "backups"
$dayFolder = Get-Date -Format "yyyy-MM-dd"
$targetDir = Join-Path $backupRoot $dayFolder
$targetDb = Join-Path $targetDir "db.sqlite3"

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
Copy-Item -LiteralPath $dbPath -Destination $targetDb -Force

$dateDirs = Get-ChildItem -Path $backupRoot -Directory -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match '^\d{4}-\d{2}-\d{2}$'
}

$ordered = $dateDirs | Sort-Object Name -Descending
$toRemove = $ordered | Select-Object -Skip $KeepDays

foreach ($dir in $toRemove) {
    Remove-Item -LiteralPath $dir.FullName -Recurse -Force
}

Write-Output ("Backup written: " + $targetDb)
Write-Output ("Retention keep days: " + $KeepDays)
Write-Output ("Backup sets kept: " + [Math]::Min($ordered.Count, $KeepDays))
