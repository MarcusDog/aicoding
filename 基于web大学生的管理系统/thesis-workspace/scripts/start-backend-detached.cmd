@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "PROJECT_ROOT=%%~fI"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "LOG_DIR=%PROJECT_ROOT%\thesis-workspace\notes"
set "LOG_FILE=%LOG_DIR%\backend-detached.log"
set "ERR_FILE=%LOG_DIR%\backend-detached.err.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%BACKEND_DIR%"
call mvnw.cmd -s .mvn\settings.xml spring-boot:run "-Dspring-boot.run.jvmArguments=-Dspring.sql.init.mode=never -Dspring.datasource.url=jdbc:h2:file:./data/volunteer;MODE=MySQL;DATABASE_TO_LOWER=TRUE;CASE_INSENSITIVE_IDENTIFIERS=TRUE" 1>>"%LOG_FILE%" 2>>"%ERR_FILE%"
