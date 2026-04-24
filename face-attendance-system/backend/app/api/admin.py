from __future__ import annotations

import csv
import io
from datetime import datetime

from flask import Blueprint, Response, request

from ..extensions import db
from ..models import CheckRule, FaceData, OperationLog, User
from ..services.statistics_service import StatisticsService
from ..utils.decorators import admin_required, get_current_admin
from ..utils.response import success_response
from ..utils.validators import parse_pagination, require_fields

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/dashboard")
@admin_required
def dashboard():
    return success_response(StatisticsService.dashboard())


@admin_bp.get("/users")
@admin_required
def list_users():
    page, size = parse_pagination(request.args)
    keyword = request.args.get("keyword", "").strip()
    department = request.args.get("department", "").strip()

    query = User.query
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((User.name.like(like)) | (User.employee_no.like(like)))
    if department:
        query = query.filter(User.department == department)

    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=size, error_out=False)
    return success_response(
        {
            "items": [user.to_dict() for user in pagination.items],
            "total": pagination.total,
            "page": page,
            "size": size,
        }
    )


@admin_bp.post("/users")
@admin_required
def create_user():
    payload = request.get_json() or {}
    require_fields(payload, ["name"])

    user = User(
        name=payload["name"],
        employee_no=payload.get("employee_no"),
        department=payload.get("department"),
        phone=payload.get("phone"),
        avatar_url=payload.get("avatar_url"),
    )
    db.session.add(user)
    db.session.commit()
    return success_response(user.to_dict(), message="user created", code=201)


@admin_bp.put("/users/<int:user_id>")
@admin_required
def update_user(user_id: int):
    payload = request.get_json() or {}
    user = User.query.get_or_404(user_id)

    for key in ["name", "employee_no", "department", "phone", "avatar_url", "status"]:
        if key in payload:
            setattr(user, key, payload[key])

    db.session.commit()
    return success_response(user.to_dict(), message="user updated")


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def disable_user(user_id: int):
    user = User.query.get_or_404(user_id)
    user.status = False
    db.session.commit()
    return success_response(user.to_dict(), message="user disabled")


@admin_bp.get("/attendance")
@admin_required
def list_attendance():
    page, size = parse_pagination(request.args)
    user_id = request.args.get("user_id")
    date_text = request.args.get("date")
    result = StatisticsService.admin_attendance_records(
        page=page,
        size=size,
        user_id=int(user_id) if user_id else None,
        date_text=date_text,
    )
    return success_response(result)


@admin_bp.get("/faces")
@admin_required
def list_faces():
    page, size = parse_pagination(request.args)
    keyword = request.args.get("keyword", "").strip()

    query = (
        db.session.query(User, FaceData)
        .outerjoin(FaceData, FaceData.user_id == User.id)
        .order_by(User.id.desc())
    )
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((User.name.like(like)) | (User.employee_no.like(like)))

    pagination = query.paginate(page=page, per_page=size, error_out=False)
    items = []
    for user, face_data in pagination.items:
        row = user.to_dict()
        row["face_data"] = face_data.to_dict() if face_data else None
        items.append(row)

    return success_response(
        {
            "items": items,
            "total": pagination.total,
            "page": page,
            "size": size,
        }
    )


@admin_bp.get("/logs")
@admin_required
def list_logs():
    page, size = parse_pagination(request.args)
    action = request.args.get("action", "").strip()
    operator_type = request.args.get("operator_type", "").strip()

    query = OperationLog.query.order_by(OperationLog.created_at.desc())
    if action:
        query = query.filter(OperationLog.action == action)
    if operator_type:
        query = query.filter(OperationLog.operator_type == operator_type)

    pagination = query.paginate(page=page, per_page=size, error_out=False)
    return success_response(
        {
            "items": [item.to_dict() for item in pagination.items],
            "total": pagination.total,
            "page": page,
            "size": size,
        }
    )


def _parse_time(value: str):
    return datetime.strptime(value, "%H:%M:%S").time()


@admin_bp.get("/rules")
@admin_required
def list_rules():
    rules = CheckRule.query.order_by(CheckRule.id.desc()).all()
    return success_response([rule.to_dict() for rule in rules])


@admin_bp.post("/rules")
@admin_required
def create_rule():
    payload = request.get_json() or {}
    require_fields(
        payload,
        ["name", "latitude", "longitude", "radius", "start_time", "end_time", "week_days"],
    )
    admin = get_current_admin()

    rule = CheckRule(
        name=payload["name"],
        admin_id=admin.id,
        latitude=float(payload["latitude"]),
        longitude=float(payload["longitude"]),
        radius=int(payload.get("radius", 200)),
        start_time=_parse_time(payload["start_time"]),
        end_time=_parse_time(payload["end_time"]),
        late_time=_parse_time(payload["late_time"]) if payload.get("late_time") else None,
        week_days=payload.get("week_days", "1,2,3,4,5"),
        is_active=bool(payload.get("is_active", True)),
    )
    db.session.add(rule)
    db.session.commit()
    return success_response(rule.to_dict(), message="rule created", code=201)


@admin_bp.put("/rules/<int:rule_id>")
@admin_required
def update_rule(rule_id: int):
    payload = request.get_json() or {}
    rule = CheckRule.query.get_or_404(rule_id)

    for key in ["name", "latitude", "longitude", "radius", "week_days", "is_active"]:
        if key in payload:
            setattr(rule, key, payload[key])

    if "start_time" in payload:
        rule.start_time = _parse_time(payload["start_time"])
    if "end_time" in payload:
        rule.end_time = _parse_time(payload["end_time"])
    if "late_time" in payload:
        rule.late_time = _parse_time(payload["late_time"]) if payload["late_time"] else None

    db.session.commit()
    return success_response(rule.to_dict(), message="rule updated")


@admin_bp.delete("/rules/<int:rule_id>")
@admin_required
def delete_rule(rule_id: int):
    rule = CheckRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    return success_response(message="rule deleted")


@admin_bp.get("/export")
@admin_required
def export_report():
    month = request.args.get("month")
    report = StatisticsService.month_summary(month)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["user_id", "name", "department", "total", "normal", "late"])
    for item in report["items"]:
        writer.writerow(
            [item["user_id"], item["name"], item["department"], item["total"], item["normal"], item["late"]]
        )

    output = buffer.getvalue()
    filename = f"attendance-report-{report['year']}-{report['month']:02d}.csv"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
