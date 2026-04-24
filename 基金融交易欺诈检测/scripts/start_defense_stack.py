from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = PROJECT_ROOT / "runtime"
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
STREAMLIT_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "streamlit.exe"


def spawn_process(command: list[str], stdout_name: str, stderr_name: str) -> int:
    stdout_path = RUNTIME_DIR / stdout_name
    stderr_path = RUNTIME_DIR / stderr_name
    with stdout_path.open("ab") as stdout_handle, stderr_path.open("ab") as stderr_handle:
        process = subprocess.Popen(
            command,
            cwd=str(PROJECT_ROOT),
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    return process.pid


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the local defense stack.")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--dashboard-port", type=int, default=8512)
    args = parser.parse_args()

    subprocess.run([str(PYTHON_EXE), "scripts/setup_kafka.py", "start"], cwd=str(PROJECT_ROOT), check=False)
    api_pid = spawn_process(
        [str(PYTHON_EXE), "scripts/run_api.py", "--host", "0.0.0.0", "--port", str(args.api_port)],
        "defense_api.out.log",
        "defense_api.err.log",
    )
    dashboard_pid = spawn_process(
        [
            str(STREAMLIT_EXE),
            "run",
            str(PROJECT_ROOT / "app" / "demo.py"),
            "--server.headless",
            "true",
            "--server.port",
            str(args.dashboard_port),
        ],
        "defense_dashboard.out.log",
        "defense_dashboard.err.log",
    )

    print(f"Kafka listener: 172.27.128.1:9092")
    print(f"API pid={api_pid} url=http://127.0.0.1:{args.api_port}")
    print(f"Dashboard pid={dashboard_pid} url=http://127.0.0.1:{args.dashboard_port}")


if __name__ == "__main__":
    main()
