from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STREAMLIT_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "streamlit.exe"
RUNTIME_DIR = PROJECT_ROOT / "runtime"


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the website presentation app.")
    parser.add_argument("--port", type=int, default=8520)
    args = parser.parse_args()

    stdout_path = RUNTIME_DIR / "site.out.log"
    stderr_path = RUNTIME_DIR / "site.err.log"
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    with stdout_path.open("ab") as stdout_handle, stderr_path.open("ab") as stderr_handle:
        process = subprocess.Popen(
            [
                str(STREAMLIT_EXE),
                "run",
                str(PROJECT_ROOT / "app" / "site.py"),
                "--server.headless",
                "true",
                "--server.port",
                str(args.port),
            ],
            cwd=str(PROJECT_ROOT),
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )

    print(f"Website pid={process.pid} url=http://127.0.0.1:{args.port}")


if __name__ == "__main__":
    main()
