from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.settings import SCREENSHOTS_DIR, ensure_directories  # noqa: E402


NPX_EXE = shutil.which("npx") or shutil.which("npx.cmd") or "npx.cmd"
PLAYWRIGHT_CLI = [NPX_EXE, "--yes", "--package", "@playwright/cli", "playwright-cli"]


def run_playwright(session: str, *args: str, check: bool = True) -> None:
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session
    subprocess.run(
        [*PLAYWRIGHT_CLI, *args],
        cwd=str(PROJECT_ROOT),
        env=env,
        check=check,
    )


def build_screenshot_code(path: Path, tab_name: str | None = None) -> str:
    parts = [
        "async (page) => {",
        "await page.setViewportSize({ width: 1440, height: 980 });",
        "await page.getByRole('heading', { name: '金融交易欺诈检测答辩看板' }).waitFor({ timeout: 20000 });",
        "await page.waitForTimeout(1200);",
    ]
    if tab_name:
        parts.extend(
            [
                f"await page.getByRole('tab', {{ name: {tab_name!r} }}).click();",
                "await page.waitForTimeout(1200);",
            ]
        )
    parts.append(f"await page.screenshot({{ path: {path.as_posix()!r} }});")
    parts.append("}")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture screenshots for the defense dashboard.")
    parser.add_argument("--url", default="http://127.0.0.1:8512")
    parser.add_argument("--output-dir", default=str(SCREENSHOTS_DIR))
    parser.add_argument("--install-browser", action="store_true")
    args = parser.parse_args()

    ensure_directories()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    session = f"defense-shot-{uuid.uuid4().hex[:8]}"

    if args.install_browser:
        run_playwright(session, "install-browser")

    targets = [
        ("defense_overview.png", None),
        ("defense_offline_prediction.png", "离线预测"),
        ("defense_streaming_monitor.png", "准实时监控"),
    ]

    try:
        run_playwright(session, "open", args.url)
        for filename, tab_name in targets:
            run_playwright(session, "run-code", build_screenshot_code(output_dir / filename, tab_name))
    finally:
        run_playwright(session, "close", check=False)

    for filename, _ in targets:
        print(output_dir / filename)


if __name__ == "__main__":
    main()
