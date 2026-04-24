$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot

python data_pipeline/run_pipeline.py

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\\start_backend.ps1"
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\\start_frontend.ps1"

Pop-Location
