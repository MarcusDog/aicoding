from __future__ import annotations

import json

import pandas as pd

from app import create_app
from app.extensions import db
from app.models.entities import AlertRecord, EventCluster, NewsArticle
from app.services.analysis import run_analysis
from app.services.cleaning import clean_news_records
from app.services.collectors import (
    OpenAPICollector,
    capped_source_limit,
    collect_news,
    flatten_source_catalog,
    list_collectable_sources,
    load_source_catalog,
)
from app.services.pipeline import sync_analysis_to_db
from app.services.storage import dataframe_to_records, write_json
from app.utils.text import extract_keywords


def test_cleaning_removes_duplicates():
    records = [
        {
            "title": "新能源车销量增长",
            "content": "<p>新能源车销量增长明显</p>",
            "summary": "新能源车销量增长明显",
            "url": "https://example.com/a",
            "source": "test",
            "publish_time": "2026-03-10 10:00:00",
        },
        {
            "title": "新能源车销量增长",
            "content": "<p>新能源车销量增长明显</p>",
            "summary": "新能源车销量增长明显",
            "url": "https://example.com/a",
            "source": "test",
            "publish_time": "2026-03-10 10:05:00",
        },
    ]
    cleaned, stats = clean_news_records(records)
    assert len(cleaned) == 1
    assert stats["strong_dedup_removed"] == 1


def test_analysis_outputs_core_tables():
    records = [
        {
            "news_id": "1",
            "title": "芯片产业合作加速",
            "content": "多家企业宣布芯片合作，产业链效率提升。",
            "summary": "芯片合作带动效率提升",
            "url": "https://example.com/1",
            "source": "demo",
            "source_type": "dataset",
            "publish_time": "2026-03-10 09:00:00",
            "crawl_time": "2026-03-10 09:10:00",
            "author": "",
            "category": "科技",
            "region": "全国",
            "keywords": ["芯片", "合作", "产业链"],
            "raw_html": "",
            "lang": "zh",
        },
        {
            "news_id": "2",
            "title": "芯片产业合作持续推进",
            "content": "产业链协同推进，市场表现回暖。",
            "summary": "产业链协同推进",
            "url": "https://example.com/2",
            "source": "demo2",
            "source_type": "dataset",
            "publish_time": "2026-03-10 11:00:00",
            "crawl_time": "2026-03-10 11:10:00",
            "author": "",
            "category": "科技",
            "region": "全国",
            "keywords": ["芯片", "合作", "回暖"],
            "raw_html": "",
            "lang": "zh",
        },
    ]
    result = run_analysis(records)
    assert not result["news_cleaned"].empty
    assert not result["hot_topics"].empty
    assert not result["keyword_trends"].empty


def test_batch_dataset_collection_from_directory(tmp_path):
    dataset_file = tmp_path / "import_news.jsonl"
    dataset_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "news_id": "import-1",
                        "title": "储能项目建设提速",
                        "content": "多个储能项目进入施工阶段。",
                        "summary": "储能项目建设提速。",
                        "url": "https://import.local/1",
                        "source": "导入测试",
                        "source_type": "dataset",
                        "publish_time": "2026-03-16 10:00:00",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "news_id": "import-2",
                        "title": "工业互联网平台应用扩展",
                        "content": "工业互联网平台在更多工厂落地。",
                        "summary": "工业互联网平台应用扩展。",
                        "url": "https://import.local/2",
                        "source": "导入测试",
                        "source_type": "dataset",
                        "publish_time": "2026-03-16 11:00:00",
                    },
                    ensure_ascii=False,
                ),
            ]
        ),
        encoding="utf-8",
    )
    records = collect_news(mode="batch", dataset_dir=tmp_path, include_batch=True, include_sample=False, include_rss=False)
    assert len(records) == 2
    assert all(item["_collect_group"] == "batch" for item in records)


def test_source_catalog_can_load_default_config():
    catalog = load_source_catalog()
    assert "rss_sources" in catalog
    assert len(flatten_source_catalog(catalog)) >= 1
    assert len(list_collectable_sources(catalog)) >= 1


def test_collectable_sources_sorted_by_priority():
    catalog = {
        "metadata": {},
        "rss_sources": [
            {"name": "低优先级", "adapter": "rss", "enabled": True, "priority": 10},
            {"name": "高优先级", "adapter": "rss", "enabled": True, "priority": 100},
        ],
        "web_sources": [],
        "partner_api_sources": [],
        "social_sources": [],
        "app_sources": [],
        "mini_program_sources": [],
    }

    items = list_collectable_sources(catalog)

    assert [item["name"] for item in items] == ["高优先级", "低优先级"]


def test_dataframe_to_records_converts_nat_to_none():
    frame = pd.DataFrame(
        [
            {
                "publish_time": pd.NaT,
                "crawl_time": pd.Timestamp("2026-03-26 10:00:00"),
                "title": "demo",
            }
        ]
    )

    rows = dataframe_to_records(frame)

    assert rows[0]["publish_time"] is None


def test_frontend_routes_can_be_served_by_flask():
    app = create_app()

    with app.test_client() as client:
        response = client.get("/")
        dashboard_response = client.get("/dashboard")

    assert response.status_code == 200
    assert dashboard_response.status_code == 200
    assert b"<div id=\"app\"></div>" in response.data


def test_extract_keywords_filters_common_english_stopwords():
    keywords = extract_keywords(
        "the and of in to iran peace talks continue and the world watches closely",
        top_k=6,
    )

    assert "the" not in keywords
    assert "and" not in keywords
    assert "of" not in keywords
    assert "iran" in keywords


def test_sync_analysis_to_db_keeps_history_and_upserts():
    app = create_app()
    news_cleaned = pd.DataFrame(
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
    news_updated = news_cleaned.copy()
    news_updated.loc[0, "summary"] = "摘要A-更新"
    news_updated.loc[0, "hot_score"] = 88.0
    second_news = pd.concat(
        [
            news_updated,
            pd.DataFrame(
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
            ),
        ],
        ignore_index=True,
    )

    empty = pd.DataFrame()
    with app.app_context():
        db.drop_all()
        db.create_all()
        sync_analysis_to_db(
            {
                "news_cleaned": news_cleaned,
                "hot_topics": empty,
                "keyword_trends": empty,
                "event_clusters": empty,
                "alerts": empty,
            }
        )
        sync_analysis_to_db(
            {
                "news_cleaned": second_news,
                "hot_topics": empty,
                "keyword_trends": empty,
                "event_clusters": empty,
                "alerts": empty,
            }
        )
        articles = NewsArticle.query.order_by(NewsArticle.news_id).all()

    assert len(articles) == 2
    assert articles[0].summary == "摘要A-更新"


def test_collect_news_supports_open_hot_api_sources(monkeypatch, tmp_path):
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "metadata": {},
                "rss_sources": [],
                "web_sources": [],
                "partner_api_sources": [
                    {
                        "name": "微博热点 API",
                        "adapter": "hot_news_api",
                        "enabled": True,
                        "url": "https://orz.ai/api/v1/dailynews/?platform=weibo",
                        "platform": "weibo",
                        "category": "社交热点",
                        "region": "中国",
                        "lang": "zh",
                    }
                ],
                "social_sources": [],
                "app_sources": [],
                "mini_program_sources": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    class FakeResponse:
        def json(self):
            return {
                "data": [
                    {
                        "title": "微博热搜测试",
                        "url": "https://example.com/weibo",
                        "content": "微博热搜测试",
                        "source": "weibo",
                        "publish_time": "2026-03-26 12:00:00",
                    }
                ]
            }

        def raise_for_status(self):
            return None

    monkeypatch.setattr("requests.sessions.Session.get", lambda *args, **kwargs: FakeResponse())

    records = collect_news(
        mode="full",
        source_config_path=catalog_path,
        sample_limit=0,
        rss_limit=0,
        web_limit=0,
        include_sample=False,
        include_batch=False,
        include_rss=False,
        include_web=False,
        include_api=True,
    )

    assert len(records) == 1
    assert records[0]["source"] == "微博热点 API"
    assert records[0]["_collect_group"] == "api"


def test_event_detail_endpoint_returns_timeline_and_fivew1h():
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()
        cluster = EventCluster(
            cluster_key="cluster-a",
            label="新能源车供应链",
            bucket_date=pd.Timestamp("2026-03-26 00:00:00").to_pydatetime(),
            news_count=2,
            representative_title="新能源车销量持续增长",
            keywords="新能源车, 供应链, 增长",
            sentiment_summary="positive",
            score=2.6,
        )
        db.session.add(cluster)
        db.session.add_all(
            [
                NewsArticle(
                    news_id="news-a",
                    title="新能源车销量持续增长，供应链协同能力提升",
                    content="上海地区新能源车销量持续增长，企业加快供应链协同与产能布局。",
                    summary="上海地区新能源车销量持续增长。",
                    url="https://example.com/a",
                    source="人民网",
                    source_type="rss",
                    publish_time=pd.Timestamp("2026-03-26 09:00:00").to_pydatetime(),
                    crawl_time=pd.Timestamp("2026-03-26 09:01:00").to_pydatetime(),
                    author="记者甲",
                    category="科技",
                    region="上海",
                    keywords="新能源车,供应链,增长",
                    raw_html="",
                    lang="zh",
                    title_hash="t1",
                    content_hash="c1",
                    simhash="1" * 16,
                    sentiment_label="positive",
                    sentiment_score=0.7,
                    event_cluster_key="cluster-a",
                    hot_score=2.8,
                ),
                NewsArticle(
                    news_id="news-b",
                    title="车企加码电池合作，新能源车产业链继续扩张",
                    content="上海和苏州多家企业围绕电池合作开展扩产，推动新能源车产业链继续扩张。",
                    summary="多家企业开展电池合作。",
                    url="https://example.com/b",
                    source="36Kr 热点",
                    source_type="web",
                    publish_time=pd.Timestamp("2026-03-26 10:30:00").to_pydatetime(),
                    crawl_time=pd.Timestamp("2026-03-26 10:31:00").to_pydatetime(),
                    author="记者乙",
                    category="科技",
                    region="上海",
                    keywords="新能源车,电池,合作",
                    raw_html="",
                    lang="zh",
                    title_hash="t2",
                    content_hash="c2",
                    simhash="2" * 16,
                    sentiment_label="positive",
                    sentiment_score=0.6,
                    event_cluster_key="cluster-a",
                    hot_score=2.4,
                ),
            ]
        )
        db.session.commit()

    with app.test_client() as client:
        response = client.get("/api/events/detail?cluster_key=cluster-a")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["cluster_key"] == "cluster-a"
    assert len(payload["timeline"]) == 2
    assert payload["fivew1h"]["where"] == "上海"
    assert payload["fivew1h"]["what"] == "新能源车销量持续增长"
    assert payload["spread_path"][0]["source"] == "人民网"


def test_alert_briefs_endpoint_returns_four_level_briefs():
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(
            AlertRecord(
                alert_type="negative_shift",
                level="严重",
                message="负面情感占比快速抬升",
                metric_value=0.62,
                bucket_time=pd.Timestamp("2026-03-26 11:00:00").to_pydatetime(),
            )
        )
        db.session.add(
            NewsArticle(
                news_id="alert-news",
                title="某行业负面舆情快速升温",
                content="多家媒体集中报道行业风险，负面情感显著上升。",
                summary="多家媒体集中报道行业风险。",
                url="https://example.com/alert",
                source="BBC World",
                source_type="rss",
                publish_time=pd.Timestamp("2026-03-26 10:55:00").to_pydatetime(),
                crawl_time=pd.Timestamp("2026-03-26 10:56:00").to_pydatetime(),
                author="Reporter",
                category="国际",
                region="全球",
                keywords="行业,风险,舆情",
                raw_html="",
                lang="zh",
                title_hash="ta",
                content_hash="ca",
                simhash="3" * 16,
                sentiment_label="negative",
                sentiment_score=-0.8,
                event_cluster_key="cluster-alert",
                hot_score=2.9,
            )
        )
        db.session.commit()

    with app.test_client() as client:
        response = client.get("/api/alerts/briefs")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload
    assert payload[0]["level"] == "严重"
    assert "应对建议" in payload[0]


def test_analysis_supports_hot_score_scenarios_and_structured_alert_levels():
    records = []
    for index in range(8):
        records.append(
            {
                "news_id": f"scenario-{index}",
                "title": f"行业风险上升引发关注 {index}",
                "content": "多家媒体报道行业风险与波动，市场情绪承压。",
                "summary": "行业风险与波动引发集中讨论。",
                "url": f"https://example.com/scenario-{index}",
                "source": "BBC World" if index < 4 else "人民网",
                "source_type": "rss",
                "publish_time": "2026-03-26 11:00:00",
                "crawl_time": "2026-03-26 11:00:30",
                "author": "",
                "category": "国际",
                "region": "全球",
                "keywords": ["风险", "波动", "预警"],
                "raw_html": "",
                "lang": "zh",
            }
        )

    result = run_analysis(records, hot_score_scenario="crisis")

    assert result["hot_score_scenario"] == "crisis"
    assert not result["alerts"].empty
    assert set(result["alerts"]["level"]).issubset({"关注", "预警", "严重", "紧急"})


def test_influence_overview_endpoint_returns_platform_region_and_network_metrics():
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(
            EventCluster(
                cluster_key="impact-cluster",
                label="科技社区讨论升温",
                bucket_date=pd.Timestamp("2026-03-26 00:00:00").to_pydatetime(),
                news_count=2,
                representative_title="开源项目在社区持续发酵",
                keywords="开源,社区,讨论",
                sentiment_summary="positive",
                score=88.0,
            )
        )
        db.session.add_all(
            [
                NewsArticle(
                    news_id="impact-a",
                    title="Hacker News 热议开源工具",
                    content="社区围绕开源工具展开讨论。",
                    summary="社区围绕开源工具展开讨论。",
                    url="https://news.ycombinator.com/item?id=1",
                    source="Hacker News Top API",
                    source_type="open_api",
                    platform="Hacker News",
                    publish_time=pd.Timestamp("2026-03-26 09:00:00").to_pydatetime(),
                    crawl_time=pd.Timestamp("2026-03-26 09:01:00").to_pydatetime(),
                    author="alice",
                    category="科技社区",
                    region="全球",
                    keywords="开源,社区,讨论",
                    raw_html="",
                    lang="en",
                    title_hash="ia",
                    content_hash="ica",
                    simhash="4" * 16,
                    sentiment_label="positive",
                    sentiment_score=0.5,
                    event_cluster_key="impact-cluster",
                    hot_score=83.0,
                    like_count=120,
                    comment_count=48,
                    share_count=0,
                    view_count=0,
                    interaction_total=168,
                ),
                NewsArticle(
                    news_id="impact-b",
                    title="Lobsters 持续跟进技术报道",
                    content="技术社区继续围绕该话题扩散。",
                    summary="技术社区继续围绕该话题扩散。",
                    url="https://lobste.rs/s/impact",
                    source="Lobsters Hottest API",
                    source_type="open_api",
                    platform="Lobsters",
                    publish_time=pd.Timestamp("2026-03-26 12:00:00").to_pydatetime(),
                    crawl_time=pd.Timestamp("2026-03-26 12:01:00").to_pydatetime(),
                    author="bob",
                    category="科技社区",
                    region="全球",
                    keywords="开源,社区,扩散",
                    raw_html="",
                    lang="en",
                    title_hash="ib",
                    content_hash="icb",
                    simhash="5" * 16,
                    sentiment_label="positive",
                    sentiment_score=0.4,
                    event_cluster_key="impact-cluster",
                    hot_score=79.0,
                    like_count=80,
                    comment_count=22,
                    share_count=0,
                    view_count=0,
                    interaction_total=102,
                ),
            ]
        )
        db.session.commit()

    with app.test_client() as client:
        response = client.get("/api/influence/overview")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["metrics"]["total_interactions"] == 270
    assert payload["platform_heat"]
    assert payload["region_heat"][0]["region"] == "全球"
    assert payload["event_influence"][0]["seed_source"] == "Hacker News Top API"
    assert payload["network"]["nodes"]
