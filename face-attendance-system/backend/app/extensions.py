from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.setdefault("RATELIMIT_STORAGE_URI", app.config.get("RATE_LIMIT_STORAGE_URI", "memory://"))
    limiter.init_app(app)

    app.config["UPLOAD_DIR"].mkdir(parents=True, exist_ok=True)
    app.config["FACE_IMAGE_DIR"].mkdir(parents=True, exist_ok=True)
    app.config["SNAPSHOT_DIR"].mkdir(parents=True, exist_ok=True)
