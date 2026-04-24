from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import Config
from app.utils.text import hash_text

AG_NEWS_URLS = {
    "train": "https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv/train.csv",
    "test": "https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv/test.csv",
}
LABEL_MAP = {"1": "World", "2": "Sports", "3": "Business", "4": "Sci/Tech"}
CATEGORY_MAP = {"1": "国际", "2": "体育", "3": "财经", "4": "科技"}


def parse_source(title: str, summary: str) -> str:
    for candidate in ("Reuters", "AP", "CNN", "Yahoo", "Washington Post", "New York Times"):
        if f"({candidate})" in title or summary.startswith(f"{candidate} -"):
            return candidate
    return "AG News Archive"


def build_record(index: int, row: list[str]) -> dict:
    label, title, summary = row[0], row[1], row[2]
    publish_time = (datetime.utcnow() - timedelta(days=index % 1825, hours=index % 24)).replace(microsecond=0)
    source = parse_source(title, summary)
    platform = source if source != "AG News Archive" else LABEL_MAP.get(label, "AG News Archive")
    return {
        "news_id": hash_text(f"ag-news|{label}|{title}|{summary[:80]}"),
        "title": title.strip(),
        "content": summary.strip(),
        "summary": summary.strip(),
        "url": "",
        "source": source,
        "source_type": "dataset",
        "platform": platform,
        "publish_time": publish_time.isoformat(),
        "crawl_time": datetime.utcnow().replace(microsecond=0).isoformat(),
        "author": "",
        "category": CATEGORY_MAP.get(label, LABEL_MAP.get(label, "综合")),
        "region": "全球",
        "lang": "en",
        "raw_html": "",
        "like_count": 0,
        "comment_count": 0,
        "share_count": 0,
        "view_count": 0,
        "interaction_total": 0,
    }


def download_rows(split: str) -> list[list[str]]:
    response = requests.get(AG_NEWS_URLS[split], timeout=60)
    response.raise_for_status()
    return list(csv.reader(io.StringIO(response.text)))


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and normalize the public AG News dataset.")
    parser.add_argument("--split", choices=["train", "test"], default="train")
    parser.add_argument("--limit", type=int, default=12000)
    parser.add_argument("--output", type=Path, default=Config.RAW_DIR / "imports" / "ag_news_archive.jsonl")
    args = parser.parse_args()

    rows = download_rows(args.split)
    selected = [build_record(index, row) for index, row in enumerate(rows[: args.limit]) if len(row) >= 3]
    write_jsonl(args.output, selected)
    print(json.dumps({"split": args.split, "written": len(selected), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
