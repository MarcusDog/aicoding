from __future__ import annotations

from app.services.cleaning import normalize_datetime
from app.services.collectors import OpenAPICollector, capped_source_limit


def test_capped_source_limit_respects_source_max_items_per_run():
    assert capped_source_limit(50, {"max_items_per_run": 12}) == 12
    assert capped_source_limit(8, {"max_items_per_run": 12}) == 8
    assert capped_source_limit(8, {}) == 8


def test_open_api_collect_source_applies_source_item_cap(monkeypatch):
    collector = OpenAPICollector()
    captured = {}

    def fake_collect_hackernews(source, limit):
        captured["limit"] = limit
        return []

    monkeypatch.setattr(collector, "collect_hackernews", fake_collect_hackernews)

    collector.collect_source({"adapter": "hackernews_api", "max_items_per_run": 12}, limit_per_source=50)

    assert captured["limit"] == 12


def test_normalize_datetime_supports_common_us_timezone_abbreviations():
    parsed = normalize_datetime("Thu, 01 Nov 2018 16:50:22 EDT")

    assert parsed is not None
    assert parsed.year == 2018
    assert parsed.month == 11
