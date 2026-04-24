from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"


def clean_lianjia_rows() -> list[dict]:
    raw_path = OUTPUT_DIR / "raw_lianjia_listings.csv"
    cleaned_rows: list[dict] = []
    seen: set[str] = set()

    with raw_path.open("r", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            external_id = row["external_id"]
            if not external_id or external_id in seen:
                continue
            seen.add(external_id)
            follow_match = re.search(r"(\d+)人关注", row["follow_info"])
            cleaned_rows.append(
                {
                    **row,
                    "follow_count": follow_match.group(1) if follow_match else "0",
                }
            )
    return cleaned_rows


def main() -> None:
    cleaned_rows = clean_lianjia_rows()
    output_path = OUTPUT_DIR / "cleaned_lianjia_listings.csv"
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
                "follow_count",
                "tags",
            ],
        )
        writer.writeheader()
        writer.writerows(cleaned_rows)
    print(f"Wrote {len(cleaned_rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
