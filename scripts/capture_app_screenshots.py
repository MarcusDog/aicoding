from __future__ import annotations

import asyncio
import socket
import subprocess
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "artifacts" / "thesis" / "screenshots"
BASE_URL = "http://127.0.0.1:8501"
CAPTURES = [
    ("fig_5_1_defense_dashboard.png", f"{BASE_URL}/?mode=thesis&page=home&product=IF&compare=IF,IH,IC,IM"),
    ("fig_5_2_market_page_if.png", f"{BASE_URL}/?mode=thesis&page=market&product=IF"),
    ("fig_5_3_trend_page_if.png", f"{BASE_URL}/?mode=thesis&page=trend&product=IF"),
    ("fig_5_4_risk_page.png", f"{BASE_URL}/?mode=thesis&page=risk&product=IF"),
    ("fig_5_5_source_page.png", f"{BASE_URL}/?mode=thesis&page=sources&product=IF"),
]


def wait_for_port(host: str, port: int, timeout: int = 60) -> None:
    started_at = time.time()
    while time.time() - started_at < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


async def capture() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/streamlit_app.py",
            "--server.headless",
            "true",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            "8501",
        ],
        cwd=ROOT,
    )
    try:
        wait_for_port("127.0.0.1", 8501, timeout=90)
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1600, "height": 980}, device_scale_factor=1.25)
            page = await context.new_page()
            for filename, url in CAPTURES:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(2500)
                await page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=60000)
                if "page=home" in url:
                    await page.wait_for_selector(".hero", timeout=60000)
                await page.wait_for_timeout(1500)
                await page.screenshot(path=str(OUTPUT_DIR / filename), full_page=False)
                print(OUTPUT_DIR / filename)
            await browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> None:
    asyncio.run(capture())


if __name__ == "__main__":
    main()
