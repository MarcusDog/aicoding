$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Invoke-IfAvailable {
  param([string]$Command, [string[]]$Arguments)
  $resolved = Get-Command $Command -ErrorAction SilentlyContinue
  if ($null -eq $resolved) {
    return $false
  }
  & $Command @Arguments
  return ($LASTEXITCODE -eq 0)
}

$py311Args = @("-3.11", "deploy_start.py") + $args
$py310Args = @("-3.10", "deploy_start.py") + $args
$pythonArgs = @("deploy_start.py") + $args

if (Invoke-IfAvailable "py" $py311Args) { exit 0 }
if (Invoke-IfAvailable "py" $py310Args) { exit 0 }
if (Invoke-IfAvailable "python" $pythonArgs) { exit $LASTEXITCODE }

Write-Host "未检测到 Python。请先安装 Python 3.11，并勾选 Add Python to PATH。" -ForegroundColor Red
exit 1
