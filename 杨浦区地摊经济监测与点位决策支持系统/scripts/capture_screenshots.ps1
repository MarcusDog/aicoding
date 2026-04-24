param(
    [string]$Python = "python",
    [string]$ServerHost = "127.0.0.1",
    [int]$Port = 8512
)

$ErrorActionPreference = "Stop"

Write-Host "Capturing dashboard screenshots..."
& $Python scripts/capture_app_screenshots.py --host $ServerHost --port $Port --python $Python
if ($LASTEXITCODE -ne 0) {
    throw "Screenshot capture failed."
}

Write-Host "Screenshot capture completed."
