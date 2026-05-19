$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$workspace = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "pdf-to-md"
$sampleSource = Join-Path $workspace "courses\sample-course\ch01\source"
New-Item -ItemType Directory -Force -Path $sampleSource | Out-Null

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

$uv = Find-Uv
if (-not $uv) {
    Write-Host "uv was not found. Run install.ps1 first."
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "pdf-to-md converter"
Write-Host "Paste a PDF or PPTX path, then press Enter."
Write-Host "Recommended: put originals under $workspace\courses\<course>\<chapter>\source"
Write-Host "Output: markdown and .reports are created under the input file folder."
Write-Host ""
$inputPath = Read-Host "File path"
$inputPath = $inputPath.Trim()
$inputPath = $inputPath.Trim('"')
$inputPath = $inputPath.Trim("'")

if (-not $inputPath) {
    Write-Host "No file path entered."
    Read-Host "Press Enter to close"
    exit 1
}

& $uv run --python 3.12 python convert.py $inputPath
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Conversion failed. Check that the file path is correct and try again."
    Read-Host "Press Enter to close"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Done. Check the markdown folder next to the input file."
Read-Host "Press Enter to close"
