$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\\backend"

if (-not (Test-Path ".venv\\Scripts\\python.exe")) {
    python -m venv .venv
}

& ".venv\\Scripts\\python.exe" -m pip install -r requirements.txt
& ".venv\\Scripts\\python.exe" manage.py migrate
& ".venv\\Scripts\\python.exe" manage.py import_sample_data
& ".venv\\Scripts\\python.exe" manage.py runserver 127.0.0.1:8000

Pop-Location
