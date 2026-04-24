from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import delete

from ..config import Config
from ..extensions import db
from ..models.entities import AlertRecord, EventCluster, HotTopic, KeywordTrend, NewsArticle
from .analysis import run_analysis
from .cleaning import clean_news_records
from .collectors import collect_news
from .storage import dataframe_to_records, write_analysis_outputs, write_json


@dataclass
class PipelineSummary:
    mode: str
    collected: int
    cleaned: int
    engine: str
    strong_dedup_removed: int
    weak_dedup_removed: int
    sample_records: int
    batch_records: int
    rss_records: int
    web_records: int
    api_records: int
    generated_at: str


def article_model_to_record(article: NewsArticle) -> dict[str, Any]:
    return {
        "news_id": article.news_id,
        "title": article.title,
        "content": article.content,
        "summary": article.summary,
        "url": article.url,
        "source": article.source,
        "source_type": article.source_type,
        "platform": article.platform,
        "publish_time": article.publish_time,
        "crawl_time": article.crawl_time,
        "author": article.author,
        "category": article.category,
        "region": article.region,
        "keywords": article.keywords.split(",") if article.keywords else [],
        "raw_html": article.raw_html,
        "lang": article.lang,
        "title_hash": article.title_hash,
        "content_hash": article.content_hash,
        "simhash": article.simhash,
        "like_count": article.like_count,
        "comment_count": article.comment_count,
        "share_count": article.share_count,
        "view_count": article.view_count,
        "interaction_total": article.interaction_total,
    }


def merge_news_records(existing_records: list[dict[str, Any]], new_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for record in existing_records:
        merged[record["news_id"]] = record
    for record in new_records:
        merged[record["news_id"]] = record
    return list(merged.values())


def load_existing_news_records() -> list[dict[str, Any]]:
    rows = NewsArticle.query.order_by(NewsArticle.publish_time.desc(), NewsArticle.crawl_time.desc()).all()
    return [article_model_to_record(row) for row in rows]


def sync_analysis_to_db(results: dict[str, Any]) -> None:
    db.create_all()
    db.session.execute(delete(HotTopic))
    db.session.execute(delete(KeywordTrend))
    db.session.execute(delete(EventCluster))
    db.session.execute(delete(AlertRecord))

    records_by_id = {}
    for record in dataframe_to_records(results["news_cleaned"]):
        if record.get("news_id"):
            records_by_id[record["news_id"]] = record

    existing_articles = {
        article.news_id: article
        for article in NewsArticle.query.filter(NewsArticle.news_id.in_(list(records_by_id.keys()))).all()
    }

    for record in records_by_id.values():
        payload = {
            "news_id": record["news_id"],
            "title": record["title"],
            "content": record["content"],
            "summary": record["summary"],
            "url": record["url"],
            "source": record["source"],
            "source_type": record["source_type"],
            "platform": record.get("platform"),
            "publish_time": record["publish_time"],
            "crawl_time": record["crawl_time"],
            "author": record["author"],
            "category": record["category"],
            "region": record["region"],
            "keywords": ",".join(record["keywords"] or []),
            "raw_html": record["raw_html"],
            "lang": record["lang"],
            "title_hash": record["title_hash"],
            "content_hash": record["content_hash"],
            "simhash": record["simhash"],
            "sentiment_label": record.get("sentiment_label"),
            "sentiment_score": record.get("sentiment_score"),
            "event_cluster_key": record.get("event_cluster_key"),
            "hot_score": record.get("hot_score"),
            "like_count": record.get("like_count", 0),
            "comment_count": record.get("comment_count", 0),
            "share_count": record.get("share_count", 0),
            "view_count": record.get("view_count", 0),
            "interaction_total": record.get("interaction_total", 0),
        }
        existing = existing_articles.get(record["news_id"])
        if existing is None:
            db.session.add(NewsArticle(**payload))
            continue
        for key, value in payload.items():
            setattr(existing, key, value)

    for row in dataframe_to_records(results["hot_topics"]):
        db.session.add(HotTopic(**row))
    for row in dataframe_to_records(results["keyword_trends"]):
        db.session.add(KeywordTrend(**row))
    for row in dataframe_to_records(results["event_clusters"]):
        db.session.add(EventCluster(**row))
    for row in dataframe_to_records(results["alerts"]):
        db.session.add(AlertRecord(**row))

    db.session.commit()


def summarize_source_types(records: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"sample_records": 0, "batch_records": 0, "rss_records": 0, "web_records": 0, "api_records": 0}
    for record in records:
        group = record.get("_collect_group")
        if group == "rss":
            summary["rss_records"] += 1
        elif group == "web":
            summary["web_records"] += 1
        elif group == "api":
            summary["api_records"] += 1
        elif group == "batch":
            summary["batch_records"] += 1
        elif group == "sample":
            summary["sample_records"] += 1
    return summary


def run_pipeline(
    mode: str = "hybrid",
    sample_limit: int = 80,
    rss_limit: int = 20,
    hot_score_scenario: str = "general",
    source_config_path: str | None = None,
    dataset_dir: str | None = None,
    dataset_paths: list[str] | None = None,
    web_limit: int = 0,
    api_limit: int = 50,
    include_sample: bool | None = None,
    include_batch: bool | None = None,
    include_rss: bool | None = None,
    include_web: bool | None = None,
    include_api: bool | None = None,
    include_history: bool = True,
    api_adapters: list[str] | None = None,
) -> dict[str, Any]:
    Config.ensure_dirs()
    raw_records = collect_news(
        mode=mode,
        sample_limit=sample_limit,
        rss_limit=rss_limit,
        source_config_path=Path(source_config_path) if source_config_path else None,
        dataset_dir=Path(dataset_dir) if dataset_dir else None,
        dataset_paths=[Path(path) for path in dataset_paths] if dataset_paths else None,
        web_limit=web_limit,
        api_limit=api_limit,
        include_sample=include_sample,
        include_batch=include_batch,
        include_rss=include_rss,
        include_web=include_web,
        include_api=include_api,
        api_adapters=api_adapters,
    )
    write_json(raw_records, Config.RAW_DIR / "latest_raw.json")
    history_dir = Config.RAW_DIR / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    write_json(raw_records, history_dir / f"raw_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json")

    cleaned_records, stats = clean_news_records(raw_records)
    if include_history:
        existing_records = load_existing_news_records()
        analysis_input = merge_news_records(existing_records, cleaned_records)
    else:
        analysis_input = cleaned_records
    analysis_results = run_analysis(analysis_input, hot_score_scenario=hot_score_scenario)
    write_analysis_outputs(analysis_results)
    sync_analysis_to_db(analysis_results)
    source_breakdown = summarize_source_types(raw_records)

    summary = PipelineSummary(
        mode=mode,
        collected=len(raw_records),
        cleaned=stats["output"],
        engine=analysis_results["engine"],
        strong_dedup_removed=stats["strong_dedup_removed"],
        weak_dedup_removed=stats["weak_dedup_removed"],
        sample_records=source_breakdown["sample_records"],
        batch_records=source_breakdown["batch_records"],
        rss_records=source_breakdown["rss_records"],
        web_records=source_breakdown["web_records"],
        api_records=source_breakdown["api_records"],
        generated_at=datetime.utcnow().isoformat(),
    )
    return {"summary": asdict(summary), "stats": stats}
