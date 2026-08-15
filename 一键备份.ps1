# Football Analysis Library - One-click Backup Script
# Place this file in the library root (D:\Cola\足球分析学习)
# Usage: right-click -> "Run with PowerShell", or run  .\一键备份.ps1
# Backups are saved to the Desktop with date-time stamp.

$ErrorActionPreference = 'Stop'

$stamp = Get-Date -Format 'yyyyMMdd_HHmm'
$desktop = [Environment]::GetFolderPath('Desktop')
$lib = $PSScriptRoot
$ark = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\_归档_旧文件'))

if (-not (Test-Path $lib)) { throw "Library not found: $lib" }
if (-not (Test-Path $ark)) { throw "Archive not found: $ark" }

$libZip = Join-Path $desktop ("Football_Library_Backup_" + $stamp + ".zip")
$arkZip = Join-Path $desktop ("Football_Archive_Backup_" + $stamp + ".zip")

Write-Host "Packing library ..."
Compress-Archive -Path (Join-Path $lib '*') -DestinationPath $libZip -Force -WarningAction SilentlyContinue

Write-Host "Packing archive ..."
Compress-Archive -Path (Join-Path $ark '*') -DestinationPath $arkZip -Force -WarningAction SilentlyContinue

$libSize = [math]::Round((Get-Item $libZip).Length / 1MB, 1)
$arkSize = [math]::Round((Get-Item $arkZip).Length / 1KB, 0)

Write-Host ""
Write-Host "Done:"
Write-Host "  $libZip  ($libSize MB)"
Write-Host "  $arkZip  ($arkSize KB)"
Write-Host ""
Write-Host "Tip: regularly copy these backups to external drive or cloud storage."