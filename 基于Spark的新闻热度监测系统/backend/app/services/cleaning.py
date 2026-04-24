from __future__ import annotations

import html
import re
from collections import defaultdict
from datetime import datetime
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from ..utils.text import build_simhash, extract_keywords, hash_text, normalize_spaces, simhash_distance, title_similarity

REGION_KEYWORDS = {
    "中国": ("中国", "北京", "上海", "深圳", "广州", "杭州", "香港"),
    "美国": ("美国", "华盛顿", "纽约", "加州", "特朗普"),
    "欧洲": ("欧洲", "英国", "法国", "德国", "欧盟", "伦敦", "巴黎"),
    "中东": ("中东", "伊朗", "以色列", "沙特", "迪拜", "霍尔木兹"),
    "亚太": ("日本", "韩国", "新加坡", "东南亚", "亚太", "澳大利亚"),
    "全球": ("world", "global", "international", "reuters", "bbc"),
}

PLATFORM_KEYWORDS = {
    "微博": ("微博", "weibo"),
    "知乎": ("知乎", "zhihu"),
    "今日头条": ("头条", "toutiao"),
    "新浪财经": ("新浪", "sina"),
    "东方财富": ("东方财富", "eastmoney"),
    "财联社": ("财联社", "cls"),
    "Guardian": ("guardian",),
    "Hacker News": ("hacker news",),
    "Lobsters": ("lobste.rs", "lobsters"),
    "BBC": ("bbc",),
    "Reuters": ("reuters",),
    "人民网": ("人民网", "人民日报"),
    "腾讯新闻": ("腾讯", "qq"),
    "网易新闻": ("网易", "163"),
    "36Kr": ("36kr",),
    "虎嗅": ("虎嗅", "huxiu"),
}

BOILERPLATE_PATTERNS = (
    re.compile(r"^\(?reuters\)?\s*[-:]\s*", re.IGNORECASE),
    re.compile(r"^\(?ap\)?\s*[-:]\s*", re.IGNORECASE),
    re.compile(r"^\(?associated press\)?\s*[-:]\s*", re.IGNORECASE),
    re.compile(r"&lt;/?b&gt;", re.IGNORECASE),
    re.compile(r"#39;"),
)
LOW_VALUE_TITLE_PATTERNS = (
    re.compile(r"责编[:：]"),
    re.compile(r"邮箱[:：]"),
    re.compile(r"请完成.*验证"),
    re.compile(r"国别频道$"),
    re.compile(r"新闻有态度$"),
    re.compile(r"网易新闻\s*国内$"),
)


TIMEZONE_ABBREVIATIONS = {
    "EDT": "-0400",
    "EST": "-0500",
    "CDT": "-0500",
    "CST": "-0600",
    "MDT": "-0600",
    "MST": "-0700",
    "PDT": "-0700",
    "PST": "-0800",
}


def clean_html(raw_html: str | None) -> str:
    if not raw_html:
        return ""
    if "<" not in raw_html and ">" not in raw_html:
        return normalize_spaces(html.unescape(raw_html))
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return normalize_spaces(html.unescape(text))


def strip_boilerplate(text: str) -> str:
    value = normalize_spaces(text)
    for pattern in BOILERPLATE_PATTERNS:
        value = pattern.sub("", value)
    value = re.sub(r"\b(source|editor|reporter|原标题|责编)\b[:：]?\s*\S*$", "", value, flags=re.IGNORECASE)
    return normalize_spaces(value)


def normalize_datetime(value: Any) -> datetime | None:
    if value in (None, "", "NaT"):
        return None
    if isinstance(value, str):
        trimmed = value.strip()
        matched = re.search(r"\b([A-Z]{3})$", trimmed)
        if matched and matched.group(1) in TIMEZONE_ABBREVIATIONS:
            abbreviation = matched.group(1)
            trimmed = re.sub(rf"\b{abbreviation}$", TIMEZONE_ABBREVIATIONS[abbreviation], trimmed)
        value = trimmed
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    timestamp = pd.Timestamp(parsed)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert(None)
    return timestamp.to_pydatetime().replace(tzinfo=None)


def normalize_int(value: Any) -> int:
    if value in (None, "", "NaN", "nan"):
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def infer_region(record: dict[str, Any], text: str) -> str:
    explicit_region = normalize_spaces(record.get("region", ""))
    if explicit_region:
        return explicit_region
    lowered = text.lower()
    for region, keywords in REGION_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return region
    return "全球"


def infer_platform(record: dict[str, Any], text: str) -> str:
    explicit_platform = normalize_spaces(record.get("platform", ""))
    if explicit_platform:
        return explicit_platform
    source = normalize_spaces(record.get("source", ""))
    lowered = f"{source} {text}".lower()
    for platform, keywords in PLATFORM_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return platform
    return source or record.get("source_type", "dataset")


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    title = strip_boilerplate(record.get("title", ""))
    content = strip_boilerplate(clean_html(record.get("content") or record.get("raw_html"))) or strip_boilerplate(
        record.get("content", "")
    )
    summary = strip_boilerplate(record.get("summary", "")) or content[:160]
    publish_time = normalize_datetime(record.get("publish_time"))
    crawl_time = normalize_datetime(record.get("crawl_time")) or datetime.utcnow()
    content = normalize_spaces(content[:1800])
    summary = normalize_spaces(summary[:220])
    merged_text = f"{title} {title} {summary} {content[:600]}"
    keywords = extract_keywords(merged_text, top_k=12)
    like_count = normalize_int(record.get("like_count"))
    comment_count = normalize_int(record.get("comment_count"))
    share_count = normalize_int(record.get("share_count"))
    view_count = normalize_int(record.get("view_count"))
    interaction_total = normalize_int(record.get("interaction_total")) or (like_count + comment_count + share_count + view_count)

    normalized = {
        "news_id": record.get("news_id") or hash_text(f"{record.get('url', '')}|{title}|{publish_time}"),
        "title": title,
        "content": content,
        "summary": summary,
        "url": record.get("url", ""),
        "source": record.get("source", "unknown"),
        "source_type": record.get("source_type", "dataset"),
        "platform": infer_platform(record, merged_text),
        "publish_time": publish_time,
        "crawl_time": crawl_time,
        "author": normalize_spaces(record.get("author", "")),
        "category": normalize_spaces(record.get("category", "")),
        "region": infer_region(record, merged_text),
        "keywords": keywords,
        "raw_html": record.get("raw_html", ""),
        "lang": record.get("lang", "zh"),
        "like_count": like_count,
        "comment_count": comment_count,
        "share_count": share_count,
        "view_count": view_count,
        "interaction_total": interaction_total,
    }
    normalized["title_hash"] = hash_text(normalized["title"])
    normalized["content_hash"] = hash_text(normalized["content"][:1000])
    normalized["simhash"] = build_simhash(f"{normalized['title']} {normalized['summary']}")
    return normalized


def is_low_value_record(record: dict[str, Any]) -> bool:
    title = record.get("title", "")
    content = record.get("content", "")
    if len(title.strip()) < 4:
        return True
    if any(pattern.search(title) for pattern in LOW_VALUE_TITLE_PATTERNS):
        return True
    if len(content.strip()) < 8 and not record.get("url"):
        return True
    return False


def clean_news_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    normalized = [normalize_record(record) for record in records]
    stats = {"input": len(records), "low_value_removed": 0, "strong_dedup_removed": 0, "weak_dedup_removed": 0, "output": 0}
    quality_records = []
    for record in normalized:
        if is_low_value_record(record):
            stats["low_value_removed"] += 1
            continue
        quality_records.append(record)

    strong_seen: set[str] = set()
    strong_deduped: list[dict[str, Any]] = []
    for record in quality_records:
        strong_key = record["url"] or record["title_hash"]
        if strong_key in strong_seen:
            stats["strong_dedup_removed"] += 1
            continue
        strong_seen.add(strong_key)
        strong_deduped.append(record)

    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    weak_deduped: list[dict[str, Any]] = []
    for record in strong_deduped:
        day_key = record["publish_time"].strftime("%Y-%m-%d") if record["publish_time"] else "unknown"
        prefix = re.sub(r"\W+", "", record["title"])[:10] or record["title_hash"][:10]
        bucket_key = f"{day_key}:{prefix}"
        candidates = buckets[bucket_key]

        is_duplicate = False
        for other in candidates:
            if simhash_distance(record["simhash"], other["simhash"]) <= 6:
                is_duplicate = True
                break
            if title_similarity(record["title"], other["title"]) >= 0.8:
                is_duplicate = True
                break

        if is_duplicate:
            stats["weak_dedup_removed"] += 1
            continue

        candidates.append(record)
        weak_deduped.append(record)

    stats["output"] = len(weak_deduped)
    return weak_deduped, stats
