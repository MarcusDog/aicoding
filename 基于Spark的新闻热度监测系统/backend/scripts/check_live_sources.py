from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.collectors import OpenAPICollector, RSSCollector, WebCollector, load_source_catalog, source_priority


def summarize_records(records: list[dict]) -> dict:
    latest = None
    if records:
        latest = max(records, key=lambda item: str(item.get("publish_time") or ""))
    return {
        "count": len(records),
        "latest_publish_time": latest.get("publish_time") if latest else None,
        "latest_title": latest.get("title") if latest else None,
        "platforms": dict(Counter(item.get("platform") or "" for item in records).most_common(5)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check realtime source routes for RSS/API/Web collectors")
    parser.add_argument("--source-config-path", type=str, default="")
    parser.add_argument("--rss-limit", type=int, default=3)
    parser.add_argument("--api-limit", type=int, default=5)
    parser.add_argument("--web-limit", type=int, default=1)
    args = parser.parse_args()

    catalog = load_source_catalog(Path(args.source_config_path) if args.source_config_path else None)
    rss_sources = sorted([item for item in catalog.get("rss_sources", []) if item.get("enabled", True)], key=source_priority)
    api_sources = sorted([item for item in catalog.get("partner_api_sources", []) if item.get("enabled", False)], key=source_priority)
    web_sources = sorted([item for item in catalog.get("web_sources", []) if item.get("enabled", False)], key=source_priority)

    rss_collector = RSSCollector()
    api_collector = OpenAPICollector()
    web_collector = WebCollector()

    report = {"rss": [], "api": [], "web": []}

    for source in rss_sources:
        started = time.perf_counter()
        records = rss_collector.collect(limit_per_source=args.rss_limit, sources=[source])
        report["rss"].append(
            {
                "name": source["name"],
                "adapter": source.get("adapter"),
                "elapsed_seconds": round(time.perf_counter() - started, 3),
                **summarize_records(records),
            }
        )

    for source in api_sources:
        started = time.perf_counter()
        records = api_collector.collect([source], limit_per_source=args.api_limit)
        report["api"].append(
            {
                "name": source["name"],
                "adapter": source.get("adapter"),
                "elapsed_seconds": round(time.perf_counter() - started, 3),
                **summarize_records(records),
            }
        )

    for source in web_sources:
        started = time.perf_counter()
        records = web_collector.collect([source], article_limit_override=args.web_limit, timeout=15)
        report["web"].append(
            {
                "name": source["name"],
                "adapter": source.get("adapter"),
                "elapsed_seconds": round(time.perf_counter() - started, 3),
                **summarize_records(records),
            }
        )

    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
