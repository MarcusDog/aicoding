from __future__ import annotations

from datetime import datetime

from sqlalchemy import Index, inspect, text

from ..extensions import db


class NewsArticle(db.Model):
    __tablename__ = "news_articles"

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    title = db.Column(db.String(512), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(1024), nullable=True, index=True)
    source = db.Column(db.String(128), nullable=False, index=True)
    source_type = db.Column(db.String(64), nullable=False, default="rss")
    platform = db.Column(db.String(64), nullable=True, index=True)
    publish_time = db.Column(db.DateTime, nullable=True, index=True)
    crawl_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.String(128), nullable=True)
    category = db.Column(db.String(128), nullable=True, index=True)
    region = db.Column(db.String(64), nullable=True)
    keywords = db.Column(db.Text, nullable=True)
    raw_html = db.Column(db.Text, nullable=True)
    lang = db.Column(db.String(16), nullable=False, default="zh")
    title_hash = db.Column(db.String(64), nullable=True, index=True)
    content_hash = db.Column(db.String(64), nullable=True, index=True)
    simhash = db.Column(db.String(32), nullable=True, index=True)
    sentiment_label = db.Column(db.String(16), nullable=True, index=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    event_cluster_key = db.Column(db.String(64), nullable=True, index=True)
    hot_score = db.Column(db.Float, nullable=True, index=True)
    like_count = db.Column(db.Integer, nullable=True, default=0)
    comment_count = db.Column(db.Integer, nullable=True, default=0)
    share_count = db.Column(db.Integer, nullable=True, default=0)
    view_count = db.Column(db.Integer, nullable=True, default=0)
    interaction_total = db.Column(db.Integer, nullable=True, default=0, index=True)

    __table_args__ = (
        Index("idx_news_source_publish_time", "source", "publish_time"),
    )


class HotTopic(db.Model):
    __tablename__ = "hot_topics"

    id = db.Column(db.Integer, primary_key=True)
    topic_label = db.Column(db.String(256), nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)
    news_count = db.Column(db.Integer, nullable=False)
    sources_count = db.Column(db.Integer, nullable=False)
    bucket_time = db.Column(db.DateTime, nullable=False, index=True)
    keywords = db.Column(db.Text, nullable=True)


class KeywordTrend(db.Model):
    __tablename__ = "keyword_trends"

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(128), nullable=False, index=True)
    bucket_time = db.Column(db.DateTime, nullable=False, index=True)
    period = db.Column(db.String(16), nullable=False, default="day")
    count = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)


class EventCluster(db.Model):
    __tablename__ = "event_clusters"

    id = db.Column(db.Integer, primary_key=True)
    cluster_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    label = db.Column(db.String(256), nullable=False)
    bucket_date = db.Column(db.DateTime, nullable=False, index=True)
    news_count = db.Column(db.Integer, nullable=False)
    representative_title = db.Column(db.String(512), nullable=False)
    keywords = db.Column(db.Text, nullable=True)
    sentiment_summary = db.Column(db.String(128), nullable=True)
    score = db.Column(db.Float, nullable=False)


class AlertRecord(db.Model):
    __tablename__ = "alert_records"

    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(64), nullable=False, index=True)
    level = db.Column(db.String(32), nullable=False, index=True)
    message = db.Column(db.String(512), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    bucket_time = db.Column(db.DateTime, nullable=False, index=True)


def ensure_schema() -> None:
    inspector = inspect(db.engine)
    if "news_articles" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("news_articles")}
    required_columns = {
        "platform": "VARCHAR(64)",
        "like_count": "INTEGER DEFAULT 0",
        "comment_count": "INTEGER DEFAULT 0",
        "share_count": "INTEGER DEFAULT 0",
        "view_count": "INTEGER DEFAULT 0",
        "interaction_total": "INTEGER DEFAULT 0",
    }

    for column_name, ddl in required_columns.items():
        if column_name not in existing_columns:
            db.session.execute(text(f"ALTER TABLE news_articles ADD COLUMN {column_name} {ddl}"))

    db.session.commit()
