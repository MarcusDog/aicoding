from __future__ import annotations

import argparse
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the local CN futures analytics stack.")
    parser.add_argument("--skip-refresh", action="store_true", help="Skip refreshing data before starting services.")
    parser.add_argument("--days", type=int, default=180, help="Backfill days used when refreshing data.")
    parser.add_argument("--api-host", default="127.0.0.1", help="API bind host.")
    parser.add_argument("--api-port", type=int, default=8000, help="API bind port.")
    parser.add_argument("--app-host", default="127.0.0.1", help="Streamlit bind host.")
    parser.add_argument("--app-port", type=int, default=8501, help="Streamlit bind port.")
    return parser.parse_args()


def wait_for_port(host: str, port: int, timeout: int = 90) -> None:
    started_at = time.time()
    while time.time() - started_at < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


def run_refresh(days: int) -> None:
    command = [sys.executable, "scripts/refresh_data.py", "--days", str(days)]
    subprocess.run(command, cwd=ROOT, check=True)


def start_process(command: list[str], env: dict[str, str] | None = None) -> subprocess.Popen[str]:
    return subprocess.Popen(command, cwd=ROOT, env=env)


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> None:
    args = parse_args()
    if not args.skip_refresh:
        run_refresh(args.days)

    api_command = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--host",
        args.api_host,
        "--port",
        str(args.api_port),
    ]
    app_command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app/streamlit_app.py",
        "--server.address",
        args.app_host,
        "--server.port",
        str(args.app_port),
        "--server.headless",
        "true",
    ]

    app_env = os.environ.copy()
    app_env["BROWSER"] = "none"

    api_process = start_process(api_command)
    app_process = start_process(app_command, env=app_env)
    try:
        wait_for_port(args.api_host, args.api_port)
        wait_for_port(args.app_host, args.app_port)
        print(f"API ready: http://{args.api_host}:{args.api_port}/docs")
        print(f"App ready: http://{args.app_host}:{args.app_port}")
        print("Press Ctrl+C to stop both services.")
        while True:
            if api_process.poll() is not None:
                raise RuntimeError("API process exited unexpectedly.")
            if app_process.poll() is not None:
                raise RuntimeError("Streamlit process exited unexpectedly.")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        terminate_process(app_process)
        terminate_process(api_process)


if __name__ == "__main__":
    if sys.platform == "win32":
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
