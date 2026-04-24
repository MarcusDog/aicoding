from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


def run_python(*args: str, check: bool = True) -> None:
    subprocess.run([str(PYTHON_EXE), *args], cwd=str(PROJECT_ROOT), check=check)


def wait_for_http(url: str, label: str, timeout_seconds: int = 60) -> None:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=5)
            if response.ok:
                return
            last_error = f"{label} returned {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"{label} not ready within {timeout_seconds}s: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the local defense-ready assets.")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--dashboard-port", type=int, default=8512)
    parser.add_argument("--rows", type=int, default=120)
    parser.add_argument("--delay", type=float, default=0.02)
    parser.add_argument("--bootstrap-servers", default="172.27.128.1:9092")
    parser.add_argument("--api-base-url", default="http://172.27.128.1:8000")
    parser.add_argument("--skip-start", action="store_true")
    parser.add_argument("--install-browser", action="store_true")
    args = parser.parse_args()

    if not args.skip_start:
        run_python(
            "scripts/start_defense_stack.py",
            "--api-port",
            str(args.api_port),
            "--dashboard-port",
            str(args.dashboard_port),
        )

    wait_for_http(f"http://127.0.0.1:{args.api_port}/health", "API")
    wait_for_http(f"http://127.0.0.1:{args.dashboard_port}", "Dashboard")

    run_python(
        "scripts/run_stream_demo.py",
        "--rows",
        str(args.rows),
        "--delay",
        str(args.delay),
        "--api-base-url",
        args.api_base_url,
        "--bootstrap-servers",
        args.bootstrap_servers,
    )
    run_python(
        "scripts/capture_dashboard_screenshots.py",
        "--url",
        f"http://127.0.0.1:{args.dashboard_port}",
        *(["--install-browser"] if args.install_browser else []),
    )
    run_python("scripts/export_thesis_assets.py")
    run_python("scripts/check_system.py")


if __name__ == "__main__":
    main()
