@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3.11 deploy_start.py %*
  if %errorlevel%==0 exit /b 0
  py -3.10 deploy_start.py %*
  if %errorlevel%==0 exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
  python deploy_start.py %*
  exit /b %errorlevel%
)

echo 未检测到 Python。请先安装 Python 3.11，并勾选 "Add Python to PATH"。
pause
exit /b 1
