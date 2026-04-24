param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "Exporting thesis figures and captions..."
& $Python scripts/export_thesis_assets.py
if ($LASTEXITCODE -ne 0) {
    throw "Asset export failed."
}

Write-Host "Asset export completed."
