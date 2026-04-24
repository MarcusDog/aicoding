from flask import Flask

from .api import register_blueprints
from .config import config_by_name
from .extensions import init_extensions
from .utils.response import error_response


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    config_name = config_name or app.config.get("ENV") or "development"
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}, 200

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValueError)
    def handle_value_error(err: ValueError):
        return error_response(str(err), code=400)

    @app.errorhandler(404)
    def handle_not_found(_):
        return error_response("resource not found", code=404)

    @app.errorhandler(500)
    def handle_server_error(_):
        return error_response("internal server error", code=500)
