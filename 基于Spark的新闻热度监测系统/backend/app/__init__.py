from __future__ import annotations

import os

from flask import Flask
from flask_cors import CORS
from flask import send_from_directory

from .config import Config
from .extensions import db


def create_app() -> Flask:
    Config.ensure_dirs()
    frontend_dist = Config.PROJECT_ROOT / "frontend" / "dist"

    app = Flask(__name__)
    app.config.from_object(Config)
    if "PYTEST_CURRENT_TEST" in os.environ:
        app.config["AUTO_FETCH_ENABLED"] = False

    CORS(app)
    db.init_app(app)

    from .models import entities  # noqa: F401
    from .api.routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        entities.ensure_schema()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.before_request
    def ensure_auto_fetch_started() -> None:
        if not app.config.get("AUTO_FETCH_ENABLED", True):
            return
        from .services.scheduler import start_realtime_scheduler

        start_realtime_scheduler(app)

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def frontend(path: str):
        requested_path = frontend_dist / path
        if path and requested_path.exists() and requested_path.is_file():
            return send_from_directory(frontend_dist, path)
        return send_from_directory(frontend_dist, "index.html")

    return app
