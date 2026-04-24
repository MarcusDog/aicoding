from __future__ import annotations

from collections import Counter
from datetime import datetime
import re
from typing import Any

import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer

from ..config import Config
from ..utils.text import extract_keywords, hash_text, is_noise_token

POSITIVE_WORDS = {
    "增长", "突破", "创新", "提升", "稳定", "回暖", "利好", "合作", "成功", "高效",
    "上涨", "修复", "签约", "落地", "开放", "扩张", "恢复", "改善", "领先", "刷新",
    "开幕", "通过", "候选", "实现", "增长点", "利率下调", "获批", "上线", "入围",
    "improve", "growth", "boost", "support", "surge", "gain", "record", "strong", "recovery",
    "deal", "launch", "expand", "profit", "rise", "wins", "win", "approved", "beats", "upgrade",
    "opens", "open", "good",
}
NEGATIVE_WORDS = {
    "下滑", "风险", "波动", "事故", "压力", "下跌", "投诉", "争议", "紧张", "预警",
    "危机", "冲突", "裁员", "暴跌", "停产", "中断", "破产", "亏损", "警报", "制裁",
    "死亡", "身亡", "遇袭", "伤人", "持刀", "强奸", "判刑", "停火失败", "绝食", "抗议",
    "crisis", "risk", "conflict", "warning", "drop", "loss", "fall", "cut", "layoff",
    "decline", "probe", "war", "attack", "slump", "ban", "rape", "jail", "crash", "victims",
    "uncertainty", "slides", "stripped", "waiting", "sue", "scared",
}
SOURCE_AUTHORITY = {
    "人民日报": 1.0,
    "人民网": 0.98,
    "新华社": 1.0,
    "新华网": 0.98,
    "BBC World": 0.92,
    "BBC Business": 0.9,
    "Reuters World": 0.95,
    "Reuters Business": 0.93,
    "Google News China": 0.75,
    "36Kr": 0.72,
    "虎嗅": 0.72,
    "腾讯新闻": 0.8,
    "网易新闻": 0.8,
    "Hacker News": 0.68,
    "Lobsters": 0.66,
}
HOT_SCORE_SCENARIOS = {
    "general": {"volume": 0.3, "sentiment": 0.25, "authority": 0.2, "interaction": 0.15, "timeliness": 0.1},
    "crisis": {"volume": 0.2, "sentiment": 0.25, "authority": 0.15, "interaction": 0.1, "timeliness": 0.3},
    "policy": {"volume": 0.2, "sentiment": 0.15, "authority": 0.35, "interaction": 0.1, "timeliness": 0.2},
}
CHINESE_FRIENDLY_SHORTLIST = {"ai", "gpu", "5g", "6g", "a股", "港股"}


def count_lexicon_hits(content: str, lexicon: set[str]) -> int:
    hits = 0
    lowered = content.lower()
    for word in lexicon:
        if re.search(r"[a-z]", word):
            if re.search(rf"\b{re.escape(word.lower())}\b", lowered):
                hits += 1
        elif word in content:
            hits += 1
    return hits


def score_sentiment(text: str) -> tuple[str, float]:
    content = (text or "").lower()
    keywords = extract_keywords(content, top_k=24)
    positive_hits = sum(1 for word in keywords if word in POSITIVE_WORDS) + count_lexicon_hits(content, POSITIVE_WORDS)
    negative_hits = sum(1 for word in keywords if word in NEGATIVE_WORDS) + count_lexicon_hits(content, NEGATIVE_WORDS)
    exclamation_bonus = min(content.count("!") + content.count("！"), 3) * 0.05
    question_bonus = min(content.count("?") + content.count("？"), 2) * 0.03
    score = positive_hits - negative_hits
    strength = abs(score)

    if score > 0:
        return "positive", min(1.0, 0.38 + strength * 0.12 + exclamation_bonus)
    if score < 0:
        return "negative", max(-1.0, -0.38 - strength * 0.12 - question_bonus)

    if any(word in content for word in ("上涨", "利好", "突破", "回暖", "合作", "纪录", "增长", "surge", "record", "growth")):
        return "positive", 0.24
    if any(word in content for word in ("下跌", "风险", "危机", "事故", "争议", "制裁", "loss", "risk", "crisis", "war")):
        return "negative", -0.24
    return "neutral", 0.0


def prepare_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["publish_time"] = normalize_datetime_series(df["publish_time"])
    df["crawl_time"] = normalize_datetime_series(df["crawl_time"])
    df["bucket_day"] = df["publish_time"].dt.floor("D").fillna(pd.Timestamp(datetime.utcnow().date()))
    df["bucket_hour"] = df["publish_time"].dt.floor("h").fillna(
        pd.Timestamp(datetime.utcnow().replace(minute=0, second=0, microsecond=0))
    )
    interaction_base = df["interaction_total"] if "interaction_total" in df.columns else pd.Series(0, index=df.index)
    df["interaction_total"] = pd.to_numeric(interaction_base, errors="coerce").fillna(0)
    sentiment_text = df["title"].fillna("") + " " + df["summary"].fillna("") + " " + df["content"].fillna("")
    df[["sentiment_label", "sentiment_score"]] = sentiment_text.apply(lambda text: pd.Series(score_sentiment(text)))
    return df


def normalize_datetime_series(series: pd.Series) -> pd.Series:
    """Parse mixed RSS/API timestamps without pandas' single-format inference dropping valid rows."""

    def parse_one(value: Any) -> pd.Timestamp:
        if value in (None, "", "NaT"):
            return pd.NaT
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return pd.NaT
        timestamp = pd.Timestamp(parsed)
        if timestamp.tzinfo is not None:
            timestamp = timestamp.tz_convert(None)
        return timestamp.tz_localize(None) if timestamp.tzinfo is not None else timestamp

    return pd.to_datetime(series.map(parse_one), errors="coerce")


def resolve_source_authority(source: str) -> float:
    if source in SOURCE_AUTHORITY:
        return SOURCE_AUTHORITY[source]
    for key, score in SOURCE_AUTHORITY.items():
        if key.lower() in (source or "").lower():
            return score
    return 0.7


def apply_hot_score(df: pd.DataFrame, scenario: str = "general") -> pd.DataFrame:
    if df.empty:
        return df

    weights = HOT_SCORE_SCENARIOS.get(scenario, HOT_SCORE_SCENARIOS["general"])
    now = pd.Timestamp.utcnow().tz_localize(None)
    publish_time = df["publish_time"].fillna(now)
    source_counts = df.groupby("source")["news_id"].transform("count")
    volume_score = (source_counts / source_counts.max()).clip(lower=0.1)
    sentiment_strength = df["sentiment_score"].abs().clip(upper=1.0)
    authority_score = df["source"].map(resolve_source_authority)
    interaction_total = df["interaction_total"].fillna(0)
    keyword_richness = df["keywords"].map(lambda keywords: min(len(keywords or []), 10) / 10)

    if interaction_total.max() > 0:
        interaction_score = (interaction_total / interaction_total.max()).clip(lower=0.02)
        interaction_score = interaction_score.where(interaction_total > 0, keyword_richness)
    else:
        interaction_score = keyword_richness

    age_hours = ((now - publish_time).dt.total_seconds() / 3600).clip(lower=0)
    timeliness_score = (1 / (1 + age_hours / 12)).clip(lower=0.05)

    df["volume_score"] = volume_score
    df["sentiment_strength"] = sentiment_strength
    df["authority_score"] = authority_score
    df["interaction_score"] = interaction_score
    df["timeliness_score"] = timeliness_score
    df["hot_score_scenario"] = scenario
    df["hot_score"] = (
        volume_score * weights["volume"]
        + sentiment_strength * weights["sentiment"]
        + authority_score * weights["authority"]
        + interaction_score * weights["interaction"]
        + timeliness_score * weights["timeliness"]
    ) * 100
    return df


def limit_records_per_group(frame: pd.DataFrame, group_field: str, recent_limit: int, archive_limit: int) -> pd.DataFrame:
    if frame.empty or group_field not in frame.columns:
        return frame
    latest = frame["publish_time"].max()
    if pd.isna(latest):
        return frame

    recent_cutoff = latest - pd.Timedelta(days=45)
    recent = frame[frame["publish_time"] >= recent_cutoff]
    archive = frame[frame["publish_time"] < recent_cutoff]

    def cap_groups(grouped_frame: pd.DataFrame, limit: int) -> pd.DataFrame:
        if grouped_frame.empty:
            return grouped_frame
        return (
            grouped_frame.sort_values(["interaction_total", "hot_score", "publish_time"], ascending=[False, False, False])
            .groupby(group_field, group_keys=False)
            .head(limit)
        )

    return pd.concat([cap_groups(recent, recent_limit), cap_groups(archive, archive_limit)], ignore_index=True)


def build_analysis_scope(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    live = df[df["source_type"] != "dataset"].copy()
    archive = df[df["source_type"] == "dataset"].copy()
    live = limit_records_per_group(live, "platform", recent_limit=80, archive_limit=24)
    live = limit_records_per_group(live, "source", recent_limit=60, archive_limit=18)
    archive = limit_records_per_group(archive, "platform", recent_limit=8, archive_limit=4)
    archive = limit_records_per_group(archive, "source", recent_limit=6, archive_limit=4)
    working = pd.concat([live, archive], ignore_index=True)
    return working.sort_values(["publish_time", "interaction_total", "hot_score"], ascending=[False, False, False])


def build_focus_scope(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    live = df[df["source_type"] != "dataset"].copy()
    zh_live = live[live["lang"] == "zh"].copy()
    en_live = live[live["lang"] != "zh"].copy()
    if len(zh_live) >= 40:
        zh_live = limit_records_per_group(zh_live, "source", recent_limit=60, archive_limit=18)
        en_live = limit_records_per_group(en_live, "source", recent_limit=8, archive_limit=4)
        return pd.concat([zh_live, en_live], ignore_index=True)
    if len(live) >= 50:
        return live
    return df


def prefers_chinese_keywords(df: pd.DataFrame) -> bool:
    if df.empty or "lang" not in df.columns:
        return False
    return int((df["lang"] == "zh").sum()) >= 40


def keyword_matches_focus(keyword: str, prefer_chinese: bool) -> bool:
    if not keyword:
        return False
    if not prefer_chinese:
        return True
    return bool(re.search(r"[\u4e00-\u9fff]", keyword)) or keyword.lower() in CHINESE_FRIENDLY_SHORTLIST


def compute_hot_topics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["topic_label", "score", "news_count", "sources_count", "bucket_time", "keywords"])

    exploded = df.explode("keywords")
    exploded = exploded[exploded["keywords"].notna()]
    exploded = exploded[~exploded["keywords"].map(is_noise_token)]
    prefer_chinese = prefers_chinese_keywords(df)
    exploded = exploded[exploded["keywords"].map(lambda item: keyword_matches_focus(item, prefer_chinese))]
    grouped = (
        exploded.groupby(["bucket_day", "keywords"])
        .agg(
            news_count=("news_id", "count"),
            sources_count=("source", "nunique"),
            hot_score=("hot_score", "mean"),
            sentiment_strength=("sentiment_score", "mean"),
        )
        .reset_index()
    )
    grouped["score"] = (
        grouped["news_count"] * 12
        + grouped["sources_count"] * 10
        + grouped["hot_score"] * 0.6
        + grouped["sentiment_strength"].abs() * 10
    )
    grouped["topic_label"] = grouped["keywords"]
    grouped["bucket_time"] = grouped["bucket_day"]
    grouped = grouped[grouped["news_count"] >= 2]
    return grouped.sort_values(["score", "news_count", "sources_count"], ascending=False).head(30)[
        ["topic_label", "score", "news_count", "sources_count", "bucket_time", "keywords"]
    ]


def compute_keyword_trends(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["keyword", "bucket_time", "period", "count", "score"])

    latest = df["publish_time"].max()
    recent_cutoff = latest - pd.Timedelta(days=30) if not pd.isna(latest) else None
    working = df[df["publish_time"] >= recent_cutoff] if recent_cutoff is not None else df
    exploded = working.explode("keywords")
    exploded = exploded[exploded["keywords"].notna()]
    exploded = exploded[~exploded["keywords"].map(is_noise_token)]
    prefer_chinese = prefers_chinese_keywords(working)
    exploded = exploded[exploded["keywords"].map(lambda item: keyword_matches_focus(item, prefer_chinese))]

    overall = (
        exploded.groupby("keywords")
        .agg(count=("news_id", "count"), score=("hot_score", "mean"))
        .reset_index()
        .sort_values(["count", "score"], ascending=False)
    )
    focus_keywords = overall[overall["count"] >= 2]["keywords"].head(20).tolist()
    if not focus_keywords:
        focus_keywords = overall["keywords"].head(20).tolist()

    focused = exploded[exploded["keywords"].isin(focus_keywords)].copy()
    focused["bucket_day"] = focused["bucket_day"].dt.floor("D")
    trends = (
        focused.groupby(["bucket_day", "keywords"])
        .agg(count=("news_id", "count"), score=("hot_score", "mean"))
        .reset_index()
        .rename(columns={"keywords": "keyword", "bucket_day": "bucket_time"})
    )
    trends["period"] = "day"
    trends["score"] = trends["score"].fillna(trends["count"])
    return trends.sort_values(["count", "score", "bucket_time"], ascending=[False, False, False]).head(200)


def compute_cluster_count(total: int) -> int:
    if total <= 3:
        return total
    return max(2, min(8, total // 3))


def compute_event_clusters(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        empty = pd.DataFrame(
            columns=[
                "cluster_key",
                "label",
                "bucket_date",
                "news_count",
                "representative_title",
                "keywords",
                "sentiment_summary",
                "score",
            ]
        )
        return empty, df

    working = df.copy()
    working["event_text"] = working["title"].fillna("") + " " + working["summary"].fillna("")
    vectorizer = TfidfVectorizer(max_features=400, min_df=1)
    matrix = vectorizer.fit_transform(working["event_text"])

    if len(working) == 1:
        labels = [0]
    else:
        cluster_count = compute_cluster_count(len(working))
        model = AgglomerativeClustering(n_clusters=cluster_count)
        labels = model.fit_predict(matrix.toarray())
    working["cluster_idx"] = labels

    rows: list[dict[str, Any]] = []
    prefer_chinese = prefers_chinese_keywords(df)
    for cluster_idx, group in working.groupby("cluster_idx"):
        all_keywords = [keyword for keywords in group["keywords"] for keyword in (keywords or [])]
        label_keywords = [
            word
            for word, _ in Counter(all_keywords).most_common(10)
            if not is_noise_token(word) and keyword_matches_focus(word, prefer_chinese)
        ]
        keyword_string = ", ".join(label_keywords[:5])
        representative_title = group.sort_values("hot_score", ascending=False).iloc[0]["title"]
        label = keyword_string or representative_title[:32]
        if len(label_keywords) < 2:
            label = representative_title[:32]
        sentiment_counter = Counter(group["sentiment_label"])
        sentiment_summary = sentiment_counter.most_common(1)[0][0] if sentiment_counter else "neutral"
        score = float(group["hot_score"].mean())
        cluster_key = hash_text(f"{cluster_idx}|{representative_title}|{group.iloc[0]['bucket_day']}")
        rows.append(
            {
                "cluster_key": cluster_key,
                "label": label,
                "bucket_date": group.iloc[0]["bucket_day"],
                "news_count": int(group.shape[0]),
                "representative_title": representative_title,
                "keywords": keyword_string,
                "sentiment_summary": sentiment_summary,
                "score": score,
            }
        )
        working.loc[group.index, "event_cluster_key"] = cluster_key

    return pd.DataFrame(rows), working


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


def compute_alerts(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["alert_type", "level", "message", "metric_value", "bucket_time"])

    latest = df["publish_time"].max()
    recent_cutoff = latest - pd.Timedelta(days=7) if not pd.isna(latest) else None
    working = df[df["publish_time"] >= recent_cutoff] if recent_cutoff is not None else df
    rows: list[dict[str, Any]] = []
    hourly_volume = (
        working.groupby("bucket_hour")
        .agg(
            count=("news_id", "count"),
            negative_ratio=("sentiment_label", lambda s: (s == "negative").mean()),
            hot_score=("hot_score", "mean"),
            source_count=("source", "nunique"),
        )
        .reset_index()
    )
    if hourly_volume.empty:
        return pd.DataFrame(columns=["alert_type", "level", "message", "metric_value", "bucket_time"])

    mean_count = hourly_volume["count"].mean()
    for _, row in hourly_volume.iterrows():
        if row["count"] >= max(5, mean_count * 1.4):
            level = classify_alert_level("hot_spike", float(row["count"]))
            rows.append(
                {
                    "alert_type": "hot_spike",
                    "level": level,
                    "message": f"{row['bucket_hour']} 新闻量显著增长，热点传播速度加快",
                    "metric_value": float(row["count"]),
                    "bucket_time": row["bucket_hour"],
                }
            )

        if row["negative_ratio"] >= 0.35:
            level = classify_alert_level("negative_shift", float(row["negative_ratio"]))
            rows.append(
                {
                    "alert_type": "negative_shift",
                    "level": level,
                    "message": f"{row['bucket_hour']} 负面情感占比上升，需要关注舆情走势",
                    "metric_value": float(row["negative_ratio"]),
                    "bucket_time": row["bucket_hour"],
                }
            )

    return pd.DataFrame(rows)


def try_run_with_spark(df: pd.DataFrame) -> str:
    if not Config.ENABLE_SPARK:
        return "pandas"
    try:
        from pyspark.sql import SparkSession

        spark = (
            SparkSession.builder.master(Config.SPARK_MASTER)
            .appName("news-monitor-analysis")
            .config("spark.ui.showConsoleProgress", "false")
            .config("spark.sql.shuffle.partitions", "1")
            .getOrCreate()
        )
        spark_df = spark.createDataFrame(df[["news_id", "source", "publish_time"]].fillna(""))
        spark_df.count()
        spark.stop()
        return "pyspark"
    except Exception:
        return "pandas"


def run_analysis(records: list[dict[str, Any]], hot_score_scenario: str = "general") -> dict[str, Any]:
    df = prepare_dataframe(records)
    if df.empty:
        empty = pd.DataFrame()
        return {
            "engine": "pandas",
            "hot_score_scenario": hot_score_scenario,
            "news_cleaned": empty,
            "hot_topics": empty,
            "keyword_trends": empty,
            "event_clusters": empty,
            "sentiment_results": empty,
            "alerts": empty,
        }

    engine = try_run_with_spark(df)
    df = apply_hot_score(df, scenario=hot_score_scenario)
    analysis_scope = build_analysis_scope(df)
    focus_scope = build_focus_scope(analysis_scope)
    cluster_results, clustered_scope = compute_event_clusters(focus_scope)
    enriched_df = df.merge(clustered_scope[["news_id", "event_cluster_key"]], on="news_id", how="left")
    hot_topics = compute_hot_topics(focus_scope)
    keyword_trends = compute_keyword_trends(focus_scope)
    sentiment_results = (
        focus_scope.groupby("sentiment_label")
        .agg(count=("news_id", "count"), avg_score=("sentiment_score", "mean"))
        .reset_index()
        .sort_values("count", ascending=False)
    )
    alerts = compute_alerts(focus_scope)

    return {
        "engine": engine,
        "hot_score_scenario": hot_score_scenario,
        "news_cleaned": enriched_df,
        "hot_topics": hot_topics,
        "keyword_trends": keyword_trends,
        "event_clusters": cluster_results,
        "sentiment_results": sentiment_results,
        "alerts": alerts,
    }
