from flask import Blueprint, request

from ..extensions import db
from ..utils.decorators import get_current_user, user_required
from ..utils.response import success_response

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/me")
@user_required
def me():
    user = get_current_user()
    return success_response(user.to_dict())


@user_bp.put("/me")
@user_required
def update_me():
    payload = request.get_json() or {}
    user = get_current_user()

    for key in ["name", "department", "phone", "avatar_url", "employee_no"]:
        if key in payload:
            setattr(user, key, payload[key])

    db.session.commit()
    return success_response(user.to_dict(), message="profile updated")
