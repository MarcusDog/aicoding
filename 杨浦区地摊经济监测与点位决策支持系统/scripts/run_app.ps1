param(
    [string]$Python = "python",
    [string]$Host = "127.0.0.1",
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"

$candidates = @(
    "app\app.py",
    "app\main.py",
    "app\streamlit_app.py"
)

$entryPoint = $null
foreach ($candidate in $candidates) {
    if (Test-Path $candidate) {
        $entryPoint = $candidate
        break
    }
}

if (-not $entryPoint) {
    throw "No Streamlit entry point found. Expected one of: $($candidates -join ', ')"
}

Write-Host "Launching Streamlit from $entryPoint"
& $Python -m streamlit run $entryPoint --server.address $Host --server.port $Port

