from __future__ import annotations

import pandas as pd

from app import create_app
from app.extensions import db
from app.models.entities import NewsArticle
from app.services.analysis import run_analysis
from app.services.pipeline import sync_analysis_to_db


def test_sync_analysis_to_db_preserves_existing_history_when_incremental_batch_is_partial():
    app = create_app()
    first_batch = pd.DataFrame(
        [
            {
                "news_id": "history-a",
                "title": "新闻A",
                "content": "内容A",
                "summary": "摘要A",
                "url": "https://example.com/a",
                "source": "人民网",
                "source_type": "rss",
                "publish_time": pd.Timestamp("2026-03-26 09:00:00"),
                "crawl_time": pd.Timestamp("2026-03-26 09:01:00"),
                "author": "",
                "category": "时政",
                "region": "北京",
                "keywords": ["新闻A"],
                "raw_html": "",
                "lang": "zh",
                "title_hash": "ha",
                "content_hash": "ca",
                "simhash": "a" * 16,
                "sentiment_label": "neutral",
                "sentiment_score": 0.0,
                "event_cluster_key": "cluster-1",
                "hot_score": 80.0,
            }
        ]
    )
    incremental_batch = pd.DataFrame(
        [
            {
                "news_id": "history-b",
                "title": "新闻B",
                "content": "内容B",
                "summary": "摘要B",
                "url": "https://example.com/b",
                "source": "BBC World",
                "source_type": "rss",
                "publish_time": pd.Timestamp("2026-03-26 10:00:00"),
                "crawl_time": pd.Timestamp("2026-03-26 10:01:00"),
                "author": "",
                "category": "国际",
                "region": "全球",
                "keywords": ["新闻B"],
                "raw_html": "",
                "lang": "zh",
                "title_hash": "hb",
                "content_hash": "cb",
                "simhash": "b" * 16,
                "sentiment_label": "positive",
                "sentiment_score": 0.6,
                "event_cluster_key": "cluster-2",
                "hot_score": 92.0,
            }
        ]
    )

    empty = pd.DataFrame()
    with app.app_context():
        db.drop_all()
        db.create_all()
        sync_analysis_to_db(
            {
                "news_cleaned": first_batch,
                "hot_topics": empty,
                "keyword_trends": empty,
                "event_clusters": empty,
                "alerts": empty,
            }
        )
        sync_analysis_to_db(
            {
                "news_cleaned": incremental_batch,
                "hot_topics": empty,
                "keyword_trends": empty,
                "event_clusters": empty,
                "alerts": empty,
            }
        )
        articles = NewsArticle.query.order_by(NewsArticle.news_id).all()

    assert len(articles) == 2
    assert [article.news_id for article in articles] == ["history-a", "history-b"]


def test_run_analysis_keeps_mixed_rss_and_api_publish_times():
    records = [
        {
            "news_id": "rss-1",
            "title": "RSS item",
            "content": "Reuters world story",
            "summary": "Reuters world story",
            "url": "https://example.com/rss-1",
            "source": "Reuters World 聚合",
            "source_type": "rss",
            "platform": "Reuters",
            "publish_time": pd.Timestamp("2026-04-17 04:15:19", tz="UTC").to_pydatetime(),
            "crawl_time": pd.Timestamp("2026-04-17 04:16:00"),
            "author": "",
            "category": "world",
            "region": "global",
            "keywords": ["reuters"],
            "raw_html": "",
            "lang": "en",
            "title_hash": "r1",
            "content_hash": "r2",
            "simhash": "c" * 16,
            "interaction_total": 0,
        },
        {
            "news_id": "api-1",
            "title": "微博热点测试",
            "content": "微博热点测试",
            "summary": "微博热点测试",
            "url": "https://example.com/api-1",
            "source": "微博热点 API",
            "source_type": "open_api",
            "platform": "微博",
            "publish_time": pd.Timestamp("2026-04-17 13:46:28").to_pydatetime(),
            "crawl_time": pd.Timestamp("2026-04-17 13:47:00"),
            "author": "",
            "category": "social",
            "region": "中国",
            "keywords": ["微博"],
            "raw_html": "",
            "lang": "zh",
            "title_hash": "a1",
            "content_hash": "a2",
            "simhash": "d" * 16,
            "interaction_total": 100,
        },
    ]

    result = run_analysis(records)
    frame = result["news_cleaned"]

    assert frame["publish_time"].notna().all()
    api_row = frame.loc[frame["news_id"] == "api-1"].iloc[0]
    assert api_row["publish_time"] == pd.Timestamp("2026-04-17 13:46:28")


def test_pipeline_endpoint_keeps_requested_multi_source_realtime_collection(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'pipeline-endpoint.db').as_posix()}")

    def fake_run_pipeline_exclusive(**kwargs):
        captured.update(kwargs)
        return {
            "summary": {
                "mode": kwargs["mode"],
                "collected": 0,
                "cleaned": 0,
                "engine": "pandas",
                "strong_dedup_removed": 0,
                "weak_dedup_removed": 0,
                "sample_records": 0,
                "batch_records": 0,
                "rss_records": 0,
                "web_records": 0,
                "api_records": 0,
                "generated_at": "2026-04-18T00:00:00",
            },
            "stats": {},
        }

    monkeypatch.setattr("app.api.routes.run_pipeline_exclusive", fake_run_pipeline_exclusive)
    app = create_app()

    with app.test_client() as client:
        response = client.post(
            "/api/pipeline/run",
            json={
                "mode": "full",
                "sample_limit": 0,
                "rss_limit": 30,
                "web_limit": 2,
                "api_limit": 40,
                "include_sample": False,
                "include_batch": False,
                "include_rss": True,
                "include_web": True,
                "include_api": True,
                "include_history": True,
            },
        )

    assert response.status_code == 200
    assert captured["include_rss"] is True
    assert captured["include_web"] is True
    assert captured["include_api"] is True
    assert captured["rss_limit"] == 30
    assert captured["web_limit"] == 2
    assert captured["api_limit"] == 40
    assert captured["api_adapters"] is None


def test_pipeline_endpoint_returns_409_when_realtime_pipeline_is_already_running(monkeypatch, tmp_path):
    from app.services.scheduler import PipelineRunBusyError
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'pipeline-busy.db').as_posix()}")

    def fake_run_pipeline_exclusive(**kwargs):
        raise PipelineRunBusyError("previous realtime collection still running")

    monkeypatch.setattr("app.api.routes.run_pipeline_exclusive", fake_run_pipeline_exclusive)
    app = create_app()

    with app.test_client() as client:
        response = client.post(
            "/api/pipeline/run",
            json={
                "mode": "full",
                "sample_limit": 0,
                "rss_limit": 30,
                "api_limit": 40,
                "include_sample": False,
                "include_batch": False,
                "include_rss": True,
                "include_web": False,
                "include_api": True,
                "include_history": True,
            },
        )

    assert response.status_code == 409
    assert "后台已有实时抓取与分析任务在运行" in response.get_json()["message"]


def test_source_catalog_exposes_large_collectable_live_pool():
    from app.services.collectors import list_collectable_sources, load_source_catalog

    catalog = load_source_catalog()
    collectable = list_collectable_sources(catalog)
    enabled_rss = [source for source in catalog["rss_sources"] if source.get("enabled")]

    assert len(enabled_rss) >= 30
    assert len(collectable) >= 45


def test_realtime_scheduler_runs_one_pipeline_with_default_live_options(monkeypatch, tmp_path):
    from app.services.scheduler import RealtimePipelineScheduler

    calls = []
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'scheduler.db').as_posix()}")
    app = create_app()

    def fake_run_pipeline(**kwargs):
        calls.append(kwargs)
        return {"summary": {"collected": 12, "cleaned": 10}}

    monkeypatch.setattr("app.services.scheduler.run_pipeline", fake_run_pipeline)

    scheduler = RealtimePipelineScheduler(app, interval_seconds=600)
    result = scheduler.run_once()

    assert result["summary"]["collected"] == 12
    assert calls == [
        {
            "mode": "full",
            "sample_limit": 0,
            "rss_limit": 30,
            "web_limit": 0,
            "api_limit": 50,
            "hot_score_scenario": "general",
            "include_sample": False,
            "include_batch": False,
            "include_rss": True,
            "include_web": False,
            "include_api": True,
            "include_history": True,
        }
    ]
