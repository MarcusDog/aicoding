from __future__ import annotations

import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from sources import LIANJIA_DISTRICTS

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_decimal(text: str) -> float:
    cleaned = text.replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else 0.0


def parse_house_info(text: str) -> dict:
    parts = [part.strip() for part in text.split("|")]
    return {
        "layout": parts[0] if len(parts) > 0 else "",
        "area": parse_decimal(parts[1]) if len(parts) > 1 else 0.0,
        "orientation": parts[2] if len(parts) > 2 else "",
        "decoration": parts[3] if len(parts) > 3 else "",
        "floor_info": parts[4] if len(parts) > 4 else "",
        "build_year": int(parse_decimal(parts[5])) if len(parts) > 5 and parse_decimal(parts[5]) else "",
    }


def collect_rows(page_count: int = 1) -> list[dict]:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    rows: list[dict] = []

    root_response = session.get("https://sh.lianjia.com/ershoufang/", timeout=30)
    root_response.raise_for_status()
    soup = BeautifulSoup(root_response.text, "html.parser")
    items = soup.select("ul.sellListContent li.clear")
    if not items:
        return rows
    for item in items:
        title_node = item.select_one(".title a")
        house_info_node = item.select_one(".address .houseInfo")
        position_nodes = item.select(".flood .positionInfo a")
        total_price_node = item.select_one(".totalPrice")
        unit_price_node = item.select_one(".unitPrice")
        follow_node = item.select_one(".followInfo")
        tag_nodes = item.select(".tag span")
        if not title_node or not house_info_node or not total_price_node or not unit_price_node:
            continue

        house_info = parse_house_info(house_info_node.get_text(" ", strip=True))
        location_text = [node.get_text(" ", strip=True) for node in position_nodes]
        community_name = location_text[0] if location_text else ""
        district_like = location_text[1] if len(location_text) > 1 else "Unknown"
        mapped_district = next((key for key in LIANJIA_DISTRICTS if district_like in key), "Unknown")
        rows.append(
            {
                "source_platform": "lianjia",
                "external_id": title_node.get("href", "").rstrip("/").split("/")[-1].replace(".html", ""),
                "title": title_node.get_text(" ", strip=True),
                "listing_url": title_node.get("href", ""),
                "district": mapped_district if mapped_district != "Unknown" else district_like,
                "subdistrict": district_like,
                "community_name": community_name,
                "total_price": parse_decimal(total_price_node.get_text(" ", strip=True)),
                "unit_price": parse_decimal(unit_price_node.get_text(" ", strip=True)),
                "area": house_info["area"],
                "layout": house_info["layout"],
                "floor_info": house_info["floor_info"],
                "orientation": house_info["orientation"],
                "decoration": house_info["decoration"],
                "build_year": house_info["build_year"],
                "follow_info": follow_node.get_text(" ", strip=True) if follow_node else "",
                "tags": "|".join(node.get_text(" ", strip=True) for node in tag_nodes),
            }
        )
    time.sleep(0.8)
    return rows


def main() -> None:
    rows = collect_rows(page_count=1)
    output_path = OUTPUT_DIR / "raw_lianjia_listings.csv"
    with output_path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "source_platform",
                "external_id",
                "title",
                "listing_url",
                "district",
                "subdistrict",
                "community_name",
                "total_price",
                "unit_price",
                "area",
                "layout",
                "floor_info",
                "orientation",
                "decoration",
                "build_year",
                "follow_info",
                "tags",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
