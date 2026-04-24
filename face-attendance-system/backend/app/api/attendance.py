from flask import Blueprint, current_app, request

from ..extensions import limiter
from ..services.attendance_service import AttendanceService
from ..services.face_service import FaceService
from ..utils.decorators import get_current_user, user_required
from ..utils.response import success_response
from ..utils.validators import parse_pagination, require_fields

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


@attendance_bp.post("/check-in")
@user_required
@limiter.limit("1/minute")
def check_in():
    payload = request.get_json() or {}
    require_fields(payload, ["image_base64", "latitude", "longitude"])

    user = get_current_user()
    if payload.get("action") and payload.get("frames_base64"):
        liveness = FaceService.verify_liveness(payload["frames_base64"], payload["action"])
        if not liveness["passed"]:
            raise ValueError("liveness verification failed")

    result = AttendanceService.check_in(
        user=user,
        image_base64=payload["image_base64"],
        latitude=float(payload["latitude"]),
        longitude=float(payload["longitude"]),
        rule_id=payload.get("rule_id"),
        device_info=payload.get("device_info"),
        snapshot_dir=current_app.config["SNAPSHOT_DIR"],
    )
    return success_response(result, message="check-in success")


@attendance_bp.get("/records")
@user_required
def records():
    user = get_current_user()
    page, size = parse_pagination(request.args)
    result = AttendanceService.get_records(user, page, size, request.args.get("date"))
    return success_response(result)


@attendance_bp.get("/today")
@user_required
def today():
    user = get_current_user()
    return success_response(AttendanceService.today_status(user))


@attendance_bp.get("/statistics")
@user_required
def statistics():
    user = get_current_user()
    month = request.args.get("month")
    return success_response(AttendanceService.monthly_statistics(user, month))
