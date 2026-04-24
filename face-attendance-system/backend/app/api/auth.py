from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from ..extensions import db
from ..extensions import limiter
from ..models import Admin, User
from ..services.auth_service import AuthService
from ..utils.response import error_response, success_response
from ..utils.validators import require_fields

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/wx-login")
@limiter.limit("20/minute")
def wx_login():
    payload = request.get_json() or {}
    require_fields(payload, ["code"])

    user_info = {
        "name": payload.get("name"),
        "avatar_url": payload.get("avatar_url"),
        "department": payload.get("department"),
    }
    user, token = AuthService.wx_login(payload["code"], user_info=user_info)
    return success_response({"token": token, "user": user.to_dict()})


@auth_bp.post("/admin-login")
@limiter.limit("10/minute")
def admin_login():
    payload = request.get_json() or {}
    require_fields(payload, ["username", "password"])
    admin, token = AuthService.admin_login(payload["username"], payload["password"])
    return success_response({"token": token, "admin": admin.to_dict()})


@auth_bp.post("/logout")
@jwt_required()
def logout():
    claims = get_jwt()
    identity = get_jwt_identity()
    operator_type = claims.get("type")
    AuthService.log_action(int(identity), operator_type, "logout", "user logout")
    db.session.commit()
    return success_response(message="logout success")


@auth_bp.get("/profile")
@jwt_required()
def profile():
    claims = get_jwt()
    identity = int(get_jwt_identity())

    if claims.get("type") == "admin":
        admin = db.session.get(Admin, identity)
        if not admin:
            return error_response("admin not found", 404)
        return success_response({"type": "admin", "profile": admin.to_dict()})

    user = db.session.get(User, identity)
    if not user:
        return error_response("user not found", 404)
    return success_response({"type": "user", "profile": user.to_dict()})
