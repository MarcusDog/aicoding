import os
from datetime import timedelta
from pathlib import Path


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///attendance.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
    }
    JSON_SORT_KEYS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRE_HOURS", "24")))

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
    FACE_IMAGE_DIR = UPLOAD_DIR / "faces"
    SNAPSHOT_DIR = UPLOAD_DIR / "snapshots"

    FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.95"))
    MIN_FACE_BRIGHTNESS = float(os.getenv("MIN_FACE_BRIGHTNESS", "40"))
    MIN_FACE_BLUR_SCORE = float(os.getenv("MIN_FACE_BLUR_SCORE", "30"))

    FACE_RECOGNIZER_BACKEND = os.getenv("FACE_RECOGNIZER_BACKEND", "facenet")
    FACE_PROJECTION_PATH = os.getenv("FACE_PROJECTION_PATH", "")
    FACE_THRESHOLD_PATH = os.getenv("FACE_THRESHOLD_PATH", "")

    WECHAT_LOGIN_MODE = os.getenv("WECHAT_LOGIN_MODE", "mock")
    WECHAT_APPID = os.getenv("WECHAT_APPID", "")
    WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
