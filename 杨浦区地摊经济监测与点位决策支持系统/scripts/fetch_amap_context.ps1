param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

& $Python -m src.pipeline.fetch_amap_context
