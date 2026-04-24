from flask import Blueprint, Flask

from .admin import admin_bp
from .attendance import attendance_bp
from .auth import auth_bp
from .face import face_bp
from .statistics import statistics_bp
from .user import user_bp


api_bp = Blueprint("api", __name__, url_prefix="/api")
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(face_bp)
api_bp.register_blueprint(attendance_bp)
api_bp.register_blueprint(admin_bp)
api_bp.register_blueprint(user_bp)
api_bp.register_blueprint(statistics_bp)


def register_blueprints(app: Flask):
    app.register_blueprint(api_bp)
