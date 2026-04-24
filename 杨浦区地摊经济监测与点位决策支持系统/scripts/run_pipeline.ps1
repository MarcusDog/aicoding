param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [string]$Label,
        [scriptblock]$Action
    )

    Write-Host $Label
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label"
    }
}

Invoke-Step "Building cleaned datasets and features..." { & $Python -m src.pipeline.build_features }
Invoke-Step "Training ranking model..." { & $Python -m src.model.train }
Invoke-Step "Generating predictions..." { & $Python -m src.model.predict }

Write-Host "Pipeline completed."
