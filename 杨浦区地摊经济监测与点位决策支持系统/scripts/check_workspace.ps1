param(
    [string[]]$RequiredPaths = @(
        "data\raw",
        "data\processed",
        "src",
        "app",
        "docs",
        "thesis",
        "evidence",
        "scripts"
    )
)

$ErrorActionPreference = "Stop"

$missing = @()
foreach ($path in $RequiredPaths) {
    if (-not (Test-Path $path)) {
        $missing += $path
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Missing paths:"
    $missing | ForEach-Object { Write-Host " - $_" }
    exit 1
}

Write-Host "Workspace structure looks correct."

