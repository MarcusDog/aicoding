from __future__ import annotations

import json
import socket
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_FILES = [
    "defense_overview.png",
    "defense_offline_prediction.png",
    "defense_streaming_monitor.png",
]


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        return sock.connect_ex((host, port)) == 0


def main() -> None:
    checks = {
        "kafka_9092": port_open("127.0.0.1", 9092),
        "api_health": False,
        "dashboard_8512": False,
        "stream_summary_exists": (PROJECT_ROOT / "artifacts" / "streaming" / "latest_summary.json").exists(),
        "thesis_manifest_exists": (PROJECT_ROOT / "reports" / "thesis_figure_manifest.md").exists(),
        "screenshots_ready": all((PROJECT_ROOT / "artifacts" / "screenshots" / name).exists() for name in SCREENSHOT_FILES),
    }
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        checks["api_health"] = response.ok
    except requests.RequestException:
        pass
    try:
        response = requests.get("http://127.0.0.1:8512", timeout=5)
        checks["dashboard_8512"] = response.ok
    except requests.RequestException:
        pass

    print(json.dumps(checks, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
