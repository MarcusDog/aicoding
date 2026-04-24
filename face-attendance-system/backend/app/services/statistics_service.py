from __future__ import annotations

from calendar import monthrange
from datetime import datetime, timedelta

from sqlalchemy import case, distinct, func

from ..models import AttendanceRecord, User
from ..utils.validators import parse_month


class StatisticsService:
    @staticmethod
    def dashboard() -> dict:
        today = datetime.now().date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        total_users = User.query.filter_by(status=True).count()
        present_users = (
            AttendanceRecord.query.filter(AttendanceRecord.check_time.between(start, end))
            .with_entities(distinct(AttendanceRecord.user_id))
            .count()
        )
        late_count = AttendanceRecord.query.filter(
            AttendanceRecord.check_time.between(start, end), AttendanceRecord.status == "late"
        ).count()

        check_in_rate = round((present_users / total_users) * 100, 2) if total_users else 0.0

        trend = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())
            count = AttendanceRecord.query.filter(AttendanceRecord.check_time.between(day_start, day_end)).count()
            trend.append({"date": day.isoformat(), "count": count})

        return {
            "today": {
                "total_users": total_users,
                "present_users": present_users,
                "late_count": late_count,
                "check_in_rate": check_in_rate,
            },
            "trend": trend,
            "pending": {
                "unregistered_faces": User.query.filter_by(is_face_registered=False, status=True).count(),
            },
        }

    @staticmethod
    def admin_attendance_records(page: int, size: int, user_id: int | None = None, date_text: str | None = None):
        query = (
            AttendanceRecord.query.join(User, User.id == AttendanceRecord.user_id)
            .add_columns(User.name.label("user_name"), User.department.label("department"))
            .order_by(AttendanceRecord.check_time.desc())
        )

        if user_id:
            query = query.filter(AttendanceRecord.user_id == user_id)

        if date_text:
            try:
                day = datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("date should be YYYY-MM-DD") from exc
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(AttendanceRecord.check_time.between(day_start, day_end))

        pagination = query.paginate(page=page, per_page=size, error_out=False)
        items = []
        for row in pagination.items:
            record, user_name, department = row
            item = record.to_dict()
            item["user_name"] = user_name
            item["department"] = department
            items.append(item)
        return {
            "items": items,
            "total": pagination.total,
            "page": page,
            "size": size,
        }

    @staticmethod
    def month_summary(month_text: str | None = None):
        year, month = parse_month(month_text)
        start = datetime(year, month, 1)
        end = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

        rows = (
            User.query.filter(User.status.is_(True))
            .outerjoin(
                AttendanceRecord,
                (AttendanceRecord.user_id == User.id)
                & (AttendanceRecord.check_time >= start)
                & (AttendanceRecord.check_time <= end),
            )
            .with_entities(
                User.id.label("user_id"),
                User.name,
                User.department,
                func.count(AttendanceRecord.id).label("total"),
                func.sum(case((AttendanceRecord.status == "normal", 1), else_=0)).label("normal"),
                func.sum(case((AttendanceRecord.status == "late", 1), else_=0)).label("late"),
            )
            .group_by(User.id, User.name, User.department)
            .order_by(User.id.asc())
            .all()
        )

        result = [
            {
                "user_id": row.user_id,
                "name": row.name,
                "department": row.department,
                "total": int(row.total or 0),
                "normal": int(row.normal or 0),
                "late": int(row.late or 0),
            }
            for row in rows
        ]

        return {
            "year": year,
            "month": month,
            "items": result,
        }
