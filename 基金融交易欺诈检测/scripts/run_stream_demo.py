from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
WSL_PROJECT_DIR = "/mnt/c/Users/lenovo/OneDrive/Desktop/毕业设计_4/基金融交易欺诈检测"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Kafka/Spark streaming demo.")
    parser.add_argument("--rows", type=int, default=120)
    parser.add_argument("--delay", type=float, default=0.02)
    parser.add_argument("--api-base-url", default="http://172.27.128.1:8000")
    parser.add_argument("--bootstrap-servers", default="172.27.128.1:9092")
    args = parser.parse_args()

    stream_command = (
        f"cd {WSL_PROJECT_DIR} && "
        f"python3 scripts/run_streaming_job.py "
        f"--timeout-seconds 60 --trigger-seconds 5 "
        f"--api-base-url {args.api_base_url} "
        f"--bootstrap-servers {args.bootstrap_servers}"
    )
    producer_command = [
        str(PYTHON_EXE),
        "scripts/replay_to_kafka.py",
        "--rows",
        str(args.rows),
        "--delay",
        str(args.delay),
        "--bootstrap-servers",
        args.bootstrap_servers,
    ]

    stream_process = subprocess.Popen(["wsl", "bash", "-lc", stream_command], cwd=str(PROJECT_ROOT))
    time.sleep(15)
    subprocess.run(producer_command, cwd=str(PROJECT_ROOT), check=False)
    stream_process.wait(timeout=120)


if __name__ == "__main__":
    main()
