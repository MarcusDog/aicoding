$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $projectRoot "backend\data"

if (Test-Path $dataDir) {
    Remove-Item $dataDir -Recurse -Force
}

Write-Host "H2 本地数据库已重置。下次启动后端时会自动执行 schema.sql 和 data.sql。"
