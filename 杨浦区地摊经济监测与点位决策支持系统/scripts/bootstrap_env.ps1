param(
    [string]$Python = "python",
    [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking Python..."
& $Python --version

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment at $VenvPath"
    & $Python -m venv $VenvPath
}

$activate = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    throw "Virtual environment activation script not found: $activate"
}

Write-Host "Environment ready."
Write-Host ("Activate it with: .\{0}\Scripts\Activate.ps1" -f $VenvPath)
Write-Host "Install project dependencies after src/app are added."
