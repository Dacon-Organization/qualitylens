param(
    [switch]$Auto
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "pdf-to-md student installer"
Write-Host "This bootstraps uv, Python, Java where possible, and connects detected AI tools automatically."
Write-Host ""

$workspace = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "pdf-to-md"

function Find-Uv {
    $cmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $candidates = @(
        (Join-Path $env:USERPROFILE ".local\bin\uv.exe"),
        (Join-Path $env:USERPROFILE ".cargo\bin\uv.exe"),
        (Join-Path $env:LOCALAPPDATA "uv\uv.exe"),
        (Join-Path $env:APPDATA "uv\uv.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

function Add-UserPath {
    param([string]$PathToAdd)
    if (-not (Test-Path $PathToAdd)) { return }
    $current = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $current) { $current = "" }
    $parts = $current -split ';' | Where-Object { $_ }
    if ($parts -notcontains $PathToAdd) {
        $newPath = if ($current) { "$current;$PathToAdd" } else { $PathToAdd }
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    }
    if (($env:Path -split ';') -notcontains $PathToAdd) {
        $env:Path = "$PathToAdd;$env:Path"
    }
}

$uv = Find-Uv
if (-not $uv) {
    Write-Host "Installing uv..."
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    Add-UserPath (Join-Path $env:USERPROFILE ".local\bin")
    Add-UserPath (Join-Path $env:USERPROFILE ".cargo\bin")
    Add-UserPath (Join-Path $env:LOCALAPPDATA "uv")
    $uv = Find-Uv
}

if (-not $uv) {
    Write-Host "uv installation failed. Check your internet connection and try again."
    Read-Host "Press Enter to close"
    exit 1
}

if ($Auto) {
    & $uv run --python 3.12 python setup.py --workspace $workspace --non-interactive --cli auto
} else {
    & $uv run --python 3.12 python setup.py --workspace $workspace
}
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Install failed. Do not use the converter yet."
    Write-Host "If this is Windows right after installing uv, restart Windows and run install.bat again."
    if (-not $Auto) { Read-Host "Press Enter to close" }
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Install finished."
Write-Host "Workspace: $workspace"
Write-Host "To convert a file, run convert.bat."
Write-Host "Results are saved under the input file folder: markdown"
Write-Host ""
Write-Host "Windows note:"
Write-Host "  If uv, python, or java is not found after this install,"
Write-Host "  open a new PowerShell window and try again."
Write-Host "  If it still fails, restart Windows and run install.bat again."
Write-Host ""
if (-not $Auto) { Read-Host "Press Enter to close" }
