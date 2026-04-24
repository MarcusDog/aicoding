from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from flask import Blueprint, current_app, jsonify, request, send_file
from sqlalchemy import func

from ..extensions import db
from ..models.entities import AlertRecord, EventCluster, HotTopic, KeywordTrend, NewsArticle
from ..services.collectors import flatten_source_catalog, list_collectable_sources, load_source_catalog
from ..services.scheduler import PipelineRunBusyError, run_pipeline_exclusive

api_bp = Blueprint("api", __name__)

SENTIMENT_LABELS = {"positive": "正面", "neutral": "中性", "negative": "负面"}
ALERT_RECOMMENDATIONS = {
    "关注": "建议持续观察传播走势，记录关键词变化并准备基础回复口径。",
    "预警": "建议启动值班响应，确认事件事实、重点媒体和主要讨论方向。",
    "严重": "建议立即组织专题研判，统一对外口径并跟踪负面扩散节点。",
    "紧急": "建议立即进入应急处置流程，形成快报并通知核心负责人决策。",
}


def get_dashboard_scope_cutoff() -> datetime | None:
    latest_publish = db.session.query(func.max(NewsArticle.publish_time)).scalar()
    if latest_publish is None:
        return None
    return latest_publish - pd.Timedelta(days=30)


def scoped_news_query():
    cutoff = get_dashboard_scope_cutoff()
    query = NewsArticle.query
    if cutoff is not None:
        query = query.filter(NewsArticle.publish_time >= cutoff)
    return query


def build_dashboard_rows(limit_per_source: int = 18) -> list[NewsArticle]:
    query = scoped_news_query().order_by(NewsArticle.publish_time.desc(), NewsArticle.hot_score.desc())
    rows = query.limit(1200).all()
    selected: list[NewsArticle] = []
    source_counts: Counter[str] = Counter()
    for row in rows:
        if source_counts[row.source] >= limit_per_source:
            continue
        source_counts[row.source] += 1
        selected.append(row)
    return selected


def load_processed_sentiment_distribution() -> list[dict]:
    path = current_app.config["PROCESSED_DIR"] / "sentiment_results.json"
    if not path.exists():
        return []
    rows = pd.read_json(path)
    if rows.empty:
        return []
    return [
        {
            "name": row["sentiment_label"] or "unknown",
            "value": int(row["count"]),
            "avg_score": round(float(row.get("avg_score", 0) or 0), 4),
        }
        for _, row in rows.iterrows()
    ]


def article_to_dict(article: NewsArticle) -> dict:
    return {
        "news_id": article.news_id,
        "title": article.title,
        "summary": article.summary,
        "source": article.source,
        "platform": article.platform,
        "category": article.category,
        "region": article.region,
        "publish_time": article.publish_time.isoformat() if article.publish_time else None,
        "sentiment_label": article.sentiment_label,
        "sentiment_score": article.sentiment_score,
        "hot_score": article.hot_score,
        "like_count": article.like_count or 0,
        "comment_count": article.comment_count or 0,
        "share_count": article.share_count or 0,
        "view_count": article.view_count or 0,
        "interaction_total": article.interaction_total or 0,
        "keywords": article.keywords.split(",") if article.keywords else [],
        "url": article.url,
    }


def apply_news_filters(query, args):
    keyword = args.get("q", "").strip()
    source = args.get("source", "").strip()
    sentiment = args.get("sentiment", "").strip()
    category = args.get("category", "").strip()
    date_from = args.get("date_from", "").strip()
    date_to = args.get("date_to", "").strip()
    hot_min = args.get("hot_min", "").strip()
    hot_max = args.get("hot_max", "").strip()

    if keyword:
        query = query.filter(
            NewsArticle.title.contains(keyword)
            | NewsArticle.summary.contains(keyword)
            | NewsArticle.keywords.contains(keyword)
        )
    if source:
        query = query.filter(NewsArticle.source == source)
    if sentiment:
        query = query.filter(NewsArticle.sentiment_label == sentiment)
    if category:
        query = query.filter(NewsArticle.category == category)
    if date_from:
        parsed_from = pd.to_datetime(date_from, errors="coerce")
        if not pd.isna(parsed_from):
            query = query.filter(NewsArticle.publish_time >= parsed_from.to_pydatetime())
    if date_to:
        parsed_to = pd.to_datetime(date_to, errors="coerce")
        if not pd.isna(parsed_to):
            query = query.filter(NewsArticle.publish_time <= parsed_to.to_pydatetime())
    if hot_min:
        try:
            query = query.filter(NewsArticle.hot_score >= float(hot_min))
        except ValueError:
            pass
    if hot_max:
        try:
            query = query.filter(NewsArticle.hot_score <= float(hot_max))
        except ValueError:
            pass
    return query


def articles_to_timeline(articles: list[NewsArticle]) -> list[dict]:
    rows = []
    for article in sorted(articles, key=lambda item: item.publish_time or item.crawl_time or datetime.min):
        rows.append(
            {
                "news_id": article.news_id,
                "title": article.title,
                "source": article.source,
                "publish_time": article.publish_time.isoformat() if article.publish_time else None,
                "sentiment_label": article.sentiment_label,
                "sentiment_display": SENTIMENT_LABELS.get(article.sentiment_label, article.sentiment_label or "未知"),
                "hot_score": article.hot_score,
                "url": article.url,
            }
        )
    return rows


def build_spread_path(articles: list[NewsArticle]) -> list[dict]:
    rows = []
    seen_sources: set[str] = set()
    for article in sorted(articles, key=lambda item: item.publish_time or item.crawl_time or datetime.min):
        if article.source in seen_sources:
            continue
        seen_sources.add(article.source)
        rows.append(
            {
                "source": article.source,
                "publish_time": article.publish_time.isoformat() if article.publish_time else None,
                "title": article.title,
            }
        )
    return rows


def summarize_event_fivew1h(cluster: EventCluster | None, articles: list[NewsArticle]) -> dict:
    regions = [article.region for article in articles if article.region]
    categories = [article.category for article in articles if article.category]
    sources = [article.source for article in articles if article.source]
    earliest = min((article.publish_time for article in articles if article.publish_time), default=None)
    latest = max((article.publish_time for article in articles if article.publish_time), default=None)
    lead_article = max(articles, key=lambda item: item.hot_score or 0, default=None)
    lead_summary = (lead_article.summary if lead_article else "") or (lead_article.content[:120] if lead_article else "")
    summary_parts = [part.strip() for part in lead_summary.replace("。", "。|").split("|") if part.strip()]

    return {
        "who": Counter(sources).most_common(3),
        "when": {
            "start": earliest.isoformat() if earliest else None,
            "end": latest.isoformat() if latest else None,
        },
        "where": Counter(regions).most_common(1)[0][0] if regions else "全网",
        "what": cluster.representative_title if cluster else (lead_article.title if lead_article else ""),
        "why": summary_parts[0] if summary_parts else "",
        "how": summary_parts[1] if len(summary_parts) > 1 else summary_parts[0] if summary_parts else "",
        "category": Counter(categories).most_common(1)[0][0] if categories else "",
    }


def build_media_tendency(articles: list[NewsArticle]) -> list[dict]:
    grouped: dict[str, list[NewsArticle]] = {}
    for article in articles:
        grouped.setdefault(article.source, []).append(article)

    rows = []
    for source, items in grouped.items():
        avg_sentiment = sum(item.sentiment_score or 0 for item in items) / len(items)
        if avg_sentiment > 0.2:
            tendency = "正面"
        elif avg_sentiment < -0.2:
            tendency = "负面"
        else:
            tendency = "中性"
        rows.append(
            {
                "source": source,
                "count": len(items),
                "avg_sentiment_score": round(avg_sentiment, 4),
                "tendency": tendency,
            }
        )
    return sorted(rows, key=lambda item: item["count"], reverse=True)


def classify_alert_level(alert_type: str, metric_value: float) -> str:
    if alert_type == "negative_shift":
        if metric_value >= 0.75:
            return "紧急"
        if metric_value >= 0.6:
            return "严重"
        if metric_value >= 0.45:
            return "预警"
        return "关注"

    if metric_value >= 12:
        return "紧急"
    if metric_value >= 8:
        return "严重"
    if metric_value >= 5:
        return "预警"
    return "关注"


def build_alert_brief(alert: AlertRecord) -> dict:
    related_articles = (
        NewsArticle.query.filter(
            NewsArticle.publish_time.is_not(None),
            NewsArticle.publish_time <= alert.bucket_time,
            NewsArticle.publish_time >= pd.Timestamp(alert.bucket_time).to_pydatetime() - pd.Timedelta(hours=6),
        )
        .order_by(NewsArticle.hot_score.desc(), NewsArticle.publish_time.desc())
        .limit(5)
        .all()
    )
    titles = [article.title for article in related_articles[:3]]
    sources = sorted({article.source for article in related_articles})
    level = alert.level or classify_alert_level(alert.alert_type, alert.metric_value)

    return {
        "alert_type": alert.alert_type,
        "level": level,
        "message": alert.message,
        "metric_value": alert.metric_value,
        "bucket_time": alert.bucket_time.isoformat(),
        "core_facts": titles,
        "sources": sources,
        "应对建议": ALERT_RECOMMENDATIONS.get(level, ALERT_RECOMMENDATIONS["关注"]),
    }


def build_role_briefs() -> dict:
    hot_topics = HotTopic.query.order_by(HotTopic.score.desc()).limit(5).all()
    top_news = NewsArticle.query.order_by(NewsArticle.hot_score.desc(), NewsArticle.publish_time.desc()).limit(10).all()
    alerts = AlertRecord.query.order_by(AlertRecord.bucket_time.desc()).limit(5).all()

    brand_mentions = [article for article in top_news if any(keyword in (article.title or "") for keyword in ("品牌", "企业", "公司"))]

    return {
        "media": {
            "hot_rank": [item.topic_label for item in hot_topics],
            "competitive_sources": sorted({article.source for article in top_news[:5]}),
            "content_clues": [article.title for article in top_news[:5]],
        },
        "pr": {
            "brand_mentions": [article.title for article in brand_mentions[:5]],
            "latest_alerts": [build_alert_brief(alert) for alert in alerts[:3]],
            "competitor_updates": [article.title for article in top_news if article.category in {"财经", "科技"}][:5],
        },
        "government": {
            "public_sentiment": [
                {"label": label or "unknown", "count": count}
                for label, count in db.session.query(NewsArticle.sentiment_label, func.count(NewsArticle.id))
                .group_by(NewsArticle.sentiment_label)
                .all()
            ],
            "sudden_events": [alert.message for alert in alerts[:5]],
            "policy_feedback": [article.title for article in top_news if article.category in {"时政", "综合"}][:5],
        },
        "research": {
            "historical_records": NewsArticle.query.count(),
            "compare_dimensions": ["热度", "情感", "来源", "类别", "区域"],
            "sample_events": [item.topic_label for item in hot_topics[:5]],
        },
    }


def serialize_metric_rows(rows, name_key: str) -> list[dict]:
    return [
        {
            name_key: (name or "未知"),
            "news_count": int(news_count or 0),
            "interaction_total": int(interaction_total or 0),
            "avg_hot_score": round(float(avg_hot_score or 0), 4),
        }
        for name, news_count, interaction_total, avg_hot_score in rows
    ]


def classify_lifecycle_stage(start_time: datetime | None, end_time: datetime | None, news_count: int) -> str:
    if start_time is None or end_time is None:
        return "观察期"
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    age_hours = max(0.0, (now - end_time).total_seconds() / 3600)
    duration_hours = max(0.1, (end_time - start_time).total_seconds() / 3600)
    velocity = news_count / duration_hours
    if age_hours <= 12 and velocity >= 1.2:
        return "爆发期"
    if age_hours <= 36:
        return "升温期"
    if age_hours <= 120:
        return "平稳期"
    return "回落期"


def compute_influence_overview() -> dict:
    region_rows = (
        db.session.query(
            NewsArticle.region,
            func.count(NewsArticle.id),
            func.coalesce(func.sum(NewsArticle.interaction_total), 0),
            func.coalesce(func.avg(NewsArticle.hot_score), 0),
        )
        .group_by(NewsArticle.region)
        .order_by(func.sum(NewsArticle.interaction_total).desc(), func.count(NewsArticle.id).desc())
        .limit(12)
        .all()
    )
    platform_rows = (
        db.session.query(
            NewsArticle.platform,
            func.count(NewsArticle.id),
            func.coalesce(func.sum(NewsArticle.interaction_total), 0),
            func.coalesce(func.avg(NewsArticle.hot_score), 0),
        )
        .group_by(NewsArticle.platform)
        .order_by(func.sum(NewsArticle.interaction_total).desc(), func.count(NewsArticle.id).desc())
        .limit(12)
        .all()
    )
    source_rows = (
        db.session.query(
            NewsArticle.source,
            func.count(NewsArticle.id),
            func.coalesce(func.sum(NewsArticle.interaction_total), 0),
            func.coalesce(func.avg(NewsArticle.hot_score), 0),
        )
        .group_by(NewsArticle.source)
        .order_by(func.sum(NewsArticle.interaction_total).desc(), func.count(NewsArticle.id).desc())
        .limit(12)
        .all()
    )

    clusters = EventCluster.query.order_by(EventCluster.score.desc()).limit(10).all()
    event_rows: list[dict] = []
    network_nodes: dict[str, dict] = {}
    network_links: dict[tuple[str, str], dict] = {}
    for cluster in clusters:
        articles = (
            NewsArticle.query.filter(NewsArticle.event_cluster_key == cluster.cluster_key)
            .order_by(NewsArticle.publish_time.asc(), NewsArticle.crawl_time.asc())
            .all()
        )
        if not articles:
            continue
        start_time = min((article.publish_time for article in articles if article.publish_time), default=None)
        end_time = max((article.publish_time for article in articles if article.publish_time), default=None)
        interactions = sum(article.interaction_total or 0 for article in articles)
        unique_sources = list(dict.fromkeys(article.source for article in articles if article.source))
        unique_platforms = sorted({article.platform or article.source_type for article in articles})
        duration_hours = max(
            0.1,
            ((end_time - start_time).total_seconds() / 3600) if start_time and end_time else 0.1,
        )
        seed_source = unique_sources[0] if unique_sources else "未知"
        event_rows.append(
            {
                "cluster_key": cluster.cluster_key,
                "label": cluster.label,
                "representative_title": cluster.representative_title,
                "seed_source": seed_source,
                "source_coverage": len(unique_sources),
                "platform_coverage": len(unique_platforms),
                "interaction_total": interactions,
                "avg_hot_score": round(float(sum((article.hot_score or 0) for article in articles) / len(articles)), 4),
                "spread_speed": round(len(articles) / duration_hours, 4),
                "lifecycle_stage": classify_lifecycle_stage(start_time, end_time, len(articles)),
            }
        )
        for article in articles:
            node = network_nodes.setdefault(
                article.source,
                {
                    "name": article.source,
                    "value": 0,
                    "platform": article.platform or article.source_type,
                    "category": article.category or "",
                },
            )
            node["value"] += max(1, int(article.interaction_total or 0) or int(article.hot_score or 0))
        for left, right in zip(unique_sources, unique_sources[1:]):
            edge = network_links.setdefault((left, right), {"source": left, "target": right, "value": 0})
            edge["value"] += 1

    total_interactions = db.session.query(func.coalesce(func.sum(NewsArticle.interaction_total), 0)).scalar() or 0
    interaction_articles = db.session.query(func.count(NewsArticle.id)).filter(NewsArticle.interaction_total > 0).scalar() or 0
    top_platform = platform_rows[0][0] if platform_rows else "未知"
    top_region = region_rows[0][0] if region_rows else "未知"

    return {
        "metrics": {
            "total_interactions": int(total_interactions),
            "articles_with_real_interactions": int(interaction_articles),
            "top_platform": top_platform or "未知",
            "top_region": top_region or "未知",
        },
        "region_heat": serialize_metric_rows(region_rows, "region"),
        "platform_heat": serialize_metric_rows(platform_rows, "platform"),
        "source_influence": serialize_metric_rows(source_rows, "source"),
        "event_influence": event_rows,
        "network": {
            "nodes": sorted(network_nodes.values(), key=lambda item: item["value"], reverse=True)[:20],
            "links": sorted(network_links.values(), key=lambda item: item["value"], reverse=True)[:30],
        },
    }


@api_bp.post("/pipeline/run")
def trigger_pipeline():
    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode", "hybrid")
    sample_limit = int(payload.get("sample_limit", 80))
    rss_limit = int(payload.get("rss_limit", 20))
    web_limit = int(payload.get("web_limit", 0))
    api_limit = int(payload.get("api_limit", 50))
    include_batch = payload.get("include_batch")
    include_rss = payload.get("include_rss")
    include_web = payload.get("include_web")
    include_api = payload.get("include_api")
    api_adapters = payload.get("api_adapters")
    fast_live = bool(payload.get("fast_live", False))
    if fast_live:
        include_rss = False
        include_web = False
        include_api = True
        rss_limit = 0
        web_limit = 0
        api_limit = min(api_limit or 8, 8)
        api_adapters = ["hot_news_api"]
    try:
        result = run_pipeline_exclusive(
            mode=mode,
            sample_limit=sample_limit,
            rss_limit=rss_limit,
            hot_score_scenario=payload.get("hot_score_scenario", "general"),
            web_limit=web_limit,
            api_limit=api_limit,
            source_config_path=payload.get("source_config_path"),
            dataset_dir=payload.get("dataset_dir"),
            dataset_paths=payload.get("dataset_paths"),
            include_sample=payload.get("include_sample"),
            include_batch=include_batch,
            include_rss=include_rss,
            include_web=include_web,
            include_api=include_api,
            include_history=payload.get("include_history", True),
            api_adapters=api_adapters,
        )
    except PipelineRunBusyError:
        return jsonify({"message": "后台已有实时抓取与分析任务在运行，请等待当前任务完成后再重试。"}), 409
    return jsonify(result)


@api_bp.get("/sources/catalog")
def sources_catalog():
    catalog = load_source_catalog()
    flattened = flatten_source_catalog(catalog)
    return jsonify(
        {
            "metadata": catalog.get("metadata", {}),
            "total_sources": len(flattened),
            "collectable_sources": len(list_collectable_sources(catalog)),
            "sections": {key: len(catalog.get(key, [])) for key in catalog.keys() if key != "metadata"},
            "items": flattened,
        }
    )


@api_bp.get("/dashboard/overview")
def dashboard_overview():
    total_news = db.session.query(func.count(NewsArticle.id)).scalar() or 0
    total_sources = db.session.query(func.count(func.distinct(NewsArticle.source))).scalar() or 0
    total_clusters = db.session.query(func.count(EventCluster.id)).scalar() or 0
    avg_hot_score = db.session.query(func.avg(NewsArticle.hot_score)).scalar() or 0
    dashboard_rows = build_dashboard_rows()
    source_distribution = Counter(row.source for row in dashboard_rows)
    sentiment_distribution = Counter((row.sentiment_label or "unknown") for row in dashboard_rows)
    hot_topics = HotTopic.query.order_by(HotTopic.score.desc()).limit(10).all()
    alerts = AlertRecord.query.order_by(AlertRecord.bucket_time.desc()).limit(10).all()
    keyword_trends = KeywordTrend.query.order_by(KeywordTrend.count.desc(), KeywordTrend.score.desc(), KeywordTrend.bucket_time.desc()).limit(50).all()
    processed_sentiment = load_processed_sentiment_distribution()

    return jsonify(
        {
            "metrics": {
                "total_news": total_news,
                "total_sources": total_sources,
                "total_clusters": total_clusters,
                "avg_hot_score": round(float(avg_hot_score), 4),
            },
            "source_distribution": [{"name": name, "value": count} for name, count in source_distribution.most_common(10)],
            "sentiment_distribution": processed_sentiment or [{"name": name, "value": count} for name, count in sentiment_distribution.items()],
            "hot_topics": [
                {
                    "topic_label": item.topic_label,
                    "score": item.score,
                    "news_count": item.news_count,
                    "sources_count": item.sources_count,
                    "bucket_time": item.bucket_time.isoformat(),
                }
                for item in hot_topics
            ],
            "keyword_trends": [
                {
                    "keyword": item.keyword,
                    "bucket_time": item.bucket_time.isoformat(),
                    "count": item.count,
                    "score": item.score,
                }
                for item in keyword_trends
            ],
            "alerts": [
                {
                    "alert_type": item.alert_type,
                    "level": item.level,
                    "message": item.message,
                    "metric_value": item.metric_value,
                    "bucket_time": item.bucket_time.isoformat(),
                }
                for item in alerts
            ],
        }
    )


@api_bp.get("/news/search")
def news_search():
    query = apply_news_filters(NewsArticle.query, request.args)
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 100)

    total = query.count()
    items = query.order_by(NewsArticle.publish_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    sources = [row[0] for row in db.session.query(func.distinct(NewsArticle.source)).order_by(NewsArticle.source).all()]
    categories = [row[0] for row in db.session.query(func.distinct(NewsArticle.category)).order_by(NewsArticle.category).all() if row[0]]
    return jsonify(
        {
            "items": [article_to_dict(item) for item in items],
            "pagination": {"page": page, "page_size": page_size, "total": total},
            "sources": sources,
            "categories": categories,
        }
    )


@api_bp.get("/hot/list")
def hot_list():
    limit = min(max(int(request.args.get("limit", 20)), 1), 100)
    items = HotTopic.query.order_by(HotTopic.score.desc()).limit(limit).all()
    return jsonify(
        [
            {
                "topic_label": item.topic_label,
                "score": item.score,
                "news_count": item.news_count,
                "sources_count": item.sources_count,
                "bucket_time": item.bucket_time.isoformat(),
                "keywords": item.keywords,
            }
            for item in items
        ]
    )


@api_bp.get("/trends/keywords")
def keyword_trends():
    limit = min(max(int(request.args.get("limit", 100)), 1), 200)
    items = KeywordTrend.query.order_by(KeywordTrend.count.desc(), KeywordTrend.score.desc(), KeywordTrend.bucket_time.desc()).limit(limit).all()
    return jsonify(
        [
            {
                "keyword": item.keyword,
                "bucket_time": item.bucket_time.isoformat(),
                "period": item.period,
                "count": item.count,
                "score": item.score,
            }
            for item in items
        ]
    )


@api_bp.get("/sentiment/summary")
def sentiment_summary():
    processed = load_processed_sentiment_distribution()
    if processed:
        return jsonify(
            [
                {"label": item["name"], "count": item["value"], "avg_score": item["avg_score"]}
                for item in processed
            ]
        )

    query = scoped_news_query()
    rows = (
        query.with_entities(NewsArticle.sentiment_label, func.count(NewsArticle.id), func.avg(NewsArticle.sentiment_score))
        .group_by(NewsArticle.sentiment_label)
        .all()
    )
    return jsonify(
        [
            {
                "label": label or "unknown",
                "count": count,
                "avg_score": round(float(avg_score or 0), 4),
            }
            for label, count, avg_score in rows
        ]
    )


@api_bp.get("/events/clusters")
def event_clusters():
    limit = min(max(int(request.args.get("limit", 20)), 1), 100)
    items = EventCluster.query.order_by(EventCluster.score.desc()).limit(limit).all()
    return jsonify(
        [
            {
                "cluster_key": item.cluster_key,
                "label": item.label,
                "bucket_date": item.bucket_date.isoformat(),
                "news_count": item.news_count,
                "representative_title": item.representative_title,
                "keywords": item.keywords.split(", ") if item.keywords else [],
                "sentiment_summary": item.sentiment_summary,
                "score": item.score,
            }
            for item in items
        ]
    )


@api_bp.get("/events/detail")
def event_detail():
    cluster_key = request.args.get("cluster_key", "").strip()
    cluster = None
    if cluster_key:
        cluster = EventCluster.query.filter_by(cluster_key=cluster_key).first()
    else:
        cluster = EventCluster.query.order_by(EventCluster.score.desc()).first()

    if cluster is None:
        return jsonify({"message": "no event cluster found"}), 404

    articles = (
        NewsArticle.query.filter(NewsArticle.event_cluster_key == cluster.cluster_key)
        .order_by(NewsArticle.publish_time.asc(), NewsArticle.crawl_time.asc())
        .all()
    )

    sentiment_breakdown = Counter(article.sentiment_label or "unknown" for article in articles)

    return jsonify(
        {
            "cluster_key": cluster.cluster_key,
            "label": cluster.label,
            "representative_title": cluster.representative_title,
            "score": cluster.score,
            "timeline": articles_to_timeline(articles),
            "spread_path": build_spread_path(articles),
            "fivew1h": summarize_event_fivew1h(cluster, articles),
            "media_tendency": build_media_tendency(articles),
            "sentiment_breakdown": [{"label": key, "count": value} for key, value in sentiment_breakdown.items()],
        }
    )


@api_bp.get("/alerts/briefs")
def alert_briefs():
    items = AlertRecord.query.order_by(AlertRecord.bucket_time.desc()).limit(10).all()
    return jsonify([build_alert_brief(item) for item in items])


@api_bp.get("/services/briefs")
def service_briefs():
    return jsonify(build_role_briefs())


@api_bp.get("/influence/overview")
def influence_overview():
    return jsonify(compute_influence_overview())


@api_bp.get("/export/news")
def export_news():
    query = apply_news_filters(NewsArticle.query, request.args)
    rows = [article_to_dict(item) for item in query.order_by(NewsArticle.publish_time.desc()).all()]
    export_dir = Path(current_app.config["EXPORT_DIR"])
    export_dir.mkdir(parents=True, exist_ok=True)
    export_format = request.args.get("format", "csv")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = export_dir / f"news_export_{timestamp}.{export_format}"
    frame = pd.DataFrame(rows)
    if export_format == "xlsx":
        frame.to_excel(path, index=False)
    else:
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    return send_file(path, as_attachment=True)
