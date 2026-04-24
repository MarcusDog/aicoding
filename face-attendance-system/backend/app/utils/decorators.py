from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from ..extensions import db
from ..models import Admin, User
from .response import error_response


def _verify_type(expected: str):
    claims = get_jwt()
    token_type = claims.get("type")
    if token_type != expected:
        return error_response("permission denied", code=403)
    return None


def user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        denied = _verify_type("user")
        if denied:
            return denied
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        denied = _verify_type("admin")
        if denied:
            return denied
        return func(*args, **kwargs)

    return wrapper


def get_current_user() -> User:
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("user not found")
    return user


def get_current_admin() -> Admin:
    admin_id = int(get_jwt_identity())
    admin = db.session.get(Admin, admin_id)
    if not admin:
        raise ValueError("admin not found")
    return admin
