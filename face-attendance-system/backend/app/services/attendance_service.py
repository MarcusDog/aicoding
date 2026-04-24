from __future__ import annotations

from calendar import monthrange
from datetime import datetime
from pathlib import Path

import cv2
from sqlalchemy import and_, func

from ..core.face_utils import base64_to_image
from ..extensions import db
from ..models import AttendanceRecord, CheckRule, User
from ..utils.location import haversine
from ..utils.validators import parse_month
from .face_service import FaceService


class AttendanceService:
    @staticmethod
    def _find_rule(rule_id: int | None = None) -> CheckRule:
        if rule_id:
            rule = CheckRule.query.filter_by(id=rule_id, is_active=True).first()
        else:
            rule = CheckRule.query.filter_by(is_active=True).order_by(CheckRule.id.desc()).first()

        if not rule:
            raise ValueError("active check rule not found")
        return rule

    @staticmethod
    def _validate_rule_time(rule: CheckRule, now: datetime):
        weekday = now.weekday() + 1
        valid_days = {int(day) for day in rule.week_days.split(",") if day.strip().isdigit()}
        if valid_days and weekday not in valid_days:
            raise ValueError("today is not in active weekdays")

        current_time = now.time()
        if current_time < rule.start_time or current_time > rule.end_time:
            raise ValueError("current time is outside check-in window")

    @staticmethod
    def _is_duplicate(user_id: int, rule_id: int, now: datetime) -> bool:
        start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        existing_count = db.session.query(func.count(AttendanceRecord.id)).filter(
            and_(
                AttendanceRecord.user_id == user_id,
                AttendanceRecord.rule_id == rule_id,
                AttendanceRecord.check_time >= start_day,
                AttendanceRecord.check_time <= end_day,
                AttendanceRecord.check_type == "in",
            )
        ).scalar()
        return (existing_count or 0) > 0

    @staticmethod
    def _save_snapshot(image_base64: str, output_dir: Path) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        image = base64_to_image(image_base64)
        filename = f"snapshot_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg"
        path = output_dir / filename
        if not cv2.imwrite(str(path), image):
            raise ValueError("failed to save snapshot")
        return str(path)

    @staticmethod
    def _resolve_status(rule: CheckRule, now: datetime) -> str:
        if rule.late_time and now.time() > rule.late_time:
            return "late"
        return "normal"

    @staticmethod
    def check_in(
        user: User,
        image_base64: str,
        latitude: float,
        longitude: float,
        rule_id: int | None,
        device_info: str | None,
        snapshot_dir: Path,
    ) -> dict:
        now = datetime.now()
        if not user.status:
            raise ValueError("user is disabled")
        if not user.is_face_registered:
            raise ValueError("face is not registered")

        rule = AttendanceService._find_rule(rule_id)
        AttendanceService._validate_rule_time(rule, now)

        distance = haversine(latitude, longitude, rule.latitude, rule.longitude)
        if distance > rule.radius:
            raise ValueError(f"outside check-in range: {distance:.1f}m")

        if AttendanceService._is_duplicate(user.id, rule.id, now):
            raise ValueError("already checked in today")

        verify_result = FaceService.verify_for_user(user, image_base64)
        if not verify_result["matched"]:
            raise ValueError("face verification failed")

        status = AttendanceService._resolve_status(rule, now)
        snapshot_path = AttendanceService._save_snapshot(image_base64, snapshot_dir)

        record = AttendanceRecord(
            user_id=user.id,
            rule_id=rule.id,
            check_time=now,
            check_type="in",
            status=status,
            latitude=latitude,
            longitude=longitude,
            face_match_score=verify_result["score"],
            face_snapshot_path=snapshot_path,
            device_info=device_info,
        )
        db.session.add(record)
        db.session.commit()

        return {
            "record": record.to_dict(),
            "distance": distance,
            "face_score": verify_result["score"],
            "status": status,
            "threshold": verify_result["threshold"],
        }

    @staticmethod
    def get_records(user: User, page: int, size: int, date_text: str | None = None):
        query = AttendanceRecord.query.filter_by(user_id=user.id).order_by(AttendanceRecord.check_time.desc())

        if date_text:
            try:
                target = datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("date should be YYYY-MM-DD") from exc
            start = target.replace(hour=0, minute=0, second=0, microsecond=0)
            end = target.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(AttendanceRecord.check_time.between(start, end))

        pagination = query.paginate(page=page, per_page=size, error_out=False)
        return {
            "items": [item.to_dict() for item in pagination.items],
            "total": pagination.total,
            "page": page,
            "size": size,
        }

    @staticmethod
    def today_status(user: User):
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        records = AttendanceRecord.query.filter(
            AttendanceRecord.user_id == user.id,
            AttendanceRecord.check_time.between(start, end),
        ).all()

        return {
            "checked_in": len(records) > 0,
            "records": [record.to_dict() for record in records],
        }

    @staticmethod
    def monthly_statistics(user: User, month_text: str | None):
        year, month = parse_month(month_text)
        start = datetime(year, month, 1)
        end = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

        records = AttendanceRecord.query.filter(
            AttendanceRecord.user_id == user.id,
            AttendanceRecord.check_time >= start,
            AttendanceRecord.check_time <= end,
        ).all()

        late_count = sum(1 for record in records if record.status == "late")
        normal_count = sum(1 for record in records if record.status == "normal")

        return {
            "year": year,
            "month": month,
            "total": len(records),
            "normal": normal_count,
            "late": late_count,
            "absent": 0,
        }
