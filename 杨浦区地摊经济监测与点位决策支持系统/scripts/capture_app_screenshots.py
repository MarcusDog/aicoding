from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import requests
from PIL import Image

try:
    from playwright.sync_api import sync_playwright
except Exception as exc:  # noqa: BLE001
    raise SystemExit(f"Playwright unavailable: {exc}")


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "evidence" / "screenshots"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture Streamlit dashboard screenshots for thesis and defense.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8512)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--entry", default=str(ROOT / "app" / "main.py"))
    parser.add_argument("--startup-timeout", type=int, default=90)
    return parser.parse_args()


def _wait_for_server(url: str, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=3)
            if response.ok:
                return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError(f"Streamlit server did not become ready: {url}")


def _server_alive(url: str) -> bool:
    try:
        response = requests.get(url, timeout=3)
        return response.ok
    except Exception:
        return False


def _start_streamlit(python: str, entry: str, host: str, port: int) -> subprocess.Popen[str]:
    log_path = ROOT / "artifacts" / "streamlit_capture.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w", encoding="utf-8")
    return subprocess.Popen(
        [
            python,
            "-m",
            "streamlit",
            "run",
            entry,
            "--server.address",
            host,
            "--server.port",
            str(port),
            "--server.headless",
            "true",
        ],
        cwd=ROOT,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _chromium_launch_kwargs() -> dict[str, object]:
    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if chrome.exists():
        return {"headless": True, "executable_path": str(chrome)}
    return {"headless": True}


def _capture(url: str) -> list[Path]:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**_chromium_launch_kwargs())
        page = browser.new_page(viewport={"width": 1600, "height": 2200}, device_scale_factor=1.2)
        page.goto(url, wait_until="domcontentloaded")
        page.locator("[data-testid='stAppViewContainer']").first.wait_for(timeout=30000)
        page.wait_for_timeout(8000)
        full_path = SCREENSHOT_DIR / "dashboard-full.png"
        page.screenshot(path=str(full_path), full_page=True)
        outputs.append(full_path)

        for label, filename in [
            ("Top3 推荐", "dashboard-top3.png"),
            ("模型诊断", "dashboard-model-diagnostics.png"),
            ("证据链", "dashboard-evidence.png"),
        ]:
            try:
                locator = page.locator(f"text={label}").first
                locator.scroll_into_view_if_needed(timeout=10000)
                page.wait_for_timeout(800)
                locator.screenshot(path=str(SCREENSHOT_DIR / filename))
                outputs.append(SCREENSHOT_DIR / filename)
            except Exception:
                continue

        browser.close()
    return outputs


def _fallback_crop_outputs(outputs: list[Path]) -> list[Path]:
    full_path = SCREENSHOT_DIR / "dashboard-full.png"
    if not full_path.exists():
        return outputs
    if len(outputs) > 1:
        return outputs

    image = Image.open(full_path)
    width, height = image.size
    slices = [
        ("dashboard-hero.png", (0, 0, width, max(int(height * 0.22), 800))),
        ("dashboard-middle.png", (0, int(height * 0.22), width, int(height * 0.62))),
        ("dashboard-bottom.png", (0, int(height * 0.62), width, height)),
    ]
    for filename, box in slices:
        cropped = image.crop(box)
        output = SCREENSHOT_DIR / filename
        cropped.save(output)
        outputs.append(output)
    return outputs


def main() -> None:
    args = parse_args()
    url = f"http://{args.host}:{args.port}"
    process: subprocess.Popen[str] | None = None
    if not _server_alive(url):
        process = _start_streamlit(args.python, args.entry, args.host, args.port)
    try:
        _wait_for_server(url, timeout_seconds=args.startup_timeout)
        outputs = _capture(url)
        outputs = _fallback_crop_outputs(outputs)
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
    print(f"captured={len(outputs)}")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
