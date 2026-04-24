from __future__ import annotations

import os
from pathlib import Path


def resolve_database_url(database_url: str, *, base_dir: Path) -> str:
    sqlite_prefix = "sqlite:///"
    if not database_url.startswith(sqlite_prefix):
        return database_url

    database_path = database_url[len(sqlite_prefix) :]
    if database_path in {"", ":memory:"}:
        return database_url

    if len(database_path) >= 3 and database_path[1] == ":" and database_path[2] in {"/", "\\"}:
        return database_url

    candidate = Path(database_path)
    if candidate.is_absolute():
        return database_url

    resolved = (base_dir / candidate).resolve()
    return f"sqlite:///{resolved.as_posix()}"


class Config:
    BACKEND_DIR = Path(__file__).resolve().parents[1]
    PROJECT_ROOT = BACKEND_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    EXPORT_DIR = DATA_DIR / "exports"
    MODELS_DIR = DATA_DIR / "models"

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = resolve_database_url(
        os.getenv(
            "DATABASE_URL",
            f"sqlite:///{(DATA_DIR / 'news_monitor.db').as_posix()}",
        ),
        base_dir=BACKEND_DIR,
    )
    SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
    ENABLE_SPARK = os.getenv("ENABLE_SPARK", "0") == "1"
    AUTO_FETCH_ENABLED = os.getenv("AUTO_FETCH_ENABLED", "1") == "1"
    AUTO_FETCH_INTERVAL_SECONDS = int(os.getenv("AUTO_FETCH_INTERVAL_SECONDS", "600"))
    AUTO_FETCH_RSS_LIMIT = int(os.getenv("AUTO_FETCH_RSS_LIMIT", "30"))
    AUTO_FETCH_API_LIMIT = int(os.getenv("AUTO_FETCH_API_LIMIT", "50"))
    AUTO_FETCH_WEB_LIMIT = int(os.getenv("AUTO_FETCH_WEB_LIMIT", "0"))

    @classmethod
    def ensure_dirs(cls) -> None:
        for path in (cls.RAW_DIR, cls.PROCESSED_DIR, cls.EXPORT_DIR, cls.MODELS_DIR):
            path.mkdir(parents=True, exist_ok=True)
