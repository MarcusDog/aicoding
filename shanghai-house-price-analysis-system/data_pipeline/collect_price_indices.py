from __future__ import annotations

import csv
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from sources import PRICE_INDEX_SOURCES

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_city(value: str) -> str:
    return value.replace("\u3000", "").replace(" ", "").strip()


def extract_month(title: str) -> str:
    match = re.search(r"(\d{4})年(\d{1,2})月份", title)
    if not match:
        raise ValueError(f"Unable to parse month from title: {title}")
    return f"{match.group(1)}-{int(match.group(2)):02d}"


def collect_rows() -> list[dict]:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    rows: list[dict] = []

    for url in PRICE_INDEX_SOURCES:
        response = session.get(url, timeout=30)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.get_text(" ", strip=True)
        stat_month = extract_month(title)
        tables = soup.select("table")
        if len(tables) < 2:
            raise ValueError(f"Expected at least 2 tables in {url}")
        table = tables[1]
        for tr in table.select("tr")[2:]:
            cells = [td.get_text(" ", strip=True) for td in tr.select("th, td")]
            if len(cells) == 8:
                city_pairs = [
                    (cells[0], cells[1], cells[2], cells[3]),
                    (cells[4], cells[5], cells[6], cells[7]),
                ]
            elif len(cells) == 6:
                city_pairs = [
                    (cells[0], cells[1], cells[2], ""),
                    (cells[3], cells[4], cells[5], ""),
                ]
            else:
                continue
            for city, mom, yoy, average in city_pairs:
                if normalize_city(city) == "上海":
                    rows.append(
                        {
                            "stat_month": stat_month,
                            "city": "Shanghai",
                            "house_type": "second_hand",
                            "size_segment": "overall",
                            "mom_index": mom,
                            "yoy_index": yoy,
                            "average_index": average,
                            "source_url": url,
                        }
                    )
    return rows


def main() -> None:
    rows = collect_rows()
    output_path = OUTPUT_DIR / "official_price_indices.csv"
    with output_path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "stat_month",
                "city",
                "house_type",
                "size_segment",
                "mom_index",
                "yoy_index",
                "average_index",
                "source_url",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
