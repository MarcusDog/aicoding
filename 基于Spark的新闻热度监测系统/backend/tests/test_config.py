from __future__ import annotations

import importlib

import app.config as config_module


def reload_config_module():
    return importlib.reload(config_module)


def test_relative_sqlite_database_url_is_resolved_from_backend_dir(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///../data/news_monitor.db")

    module = reload_config_module()

    expected = (module.Config.BACKEND_DIR / ".." / "data" / "news_monitor.db").resolve().as_posix()
    assert module.Config.SQLALCHEMY_DATABASE_URI == f"sqlite:///{expected}"


def test_absolute_sqlite_database_url_is_preserved(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///C:/demo/news_monitor.db")

    module = reload_config_module()

    assert module.Config.SQLALCHEMY_DATABASE_URI == "sqlite:///C:/demo/news_monitor.db"


def test_non_sqlite_database_url_is_preserved(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://user:pass@127.0.0.1:3306/news_monitor")

    module = reload_config_module()

    assert module.Config.SQLALCHEMY_DATABASE_URI == "mysql+pymysql://user:pass@127.0.0.1:3306/news_monitor"
