$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $projectRoot "backend")
.\mvnw.cmd -s .mvn\settings.xml spring-boot:run
