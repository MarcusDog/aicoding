from datetime import UTC, datetime

from ..extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


from .admin import Admin  # noqa: E402,F401
from .attendance import AttendanceRecord  # noqa: E402,F401
from .check_rule import CheckRule  # noqa: E402,F401
from .face_data import FaceData  # noqa: E402,F401
from .operation_log import OperationLog  # noqa: E402,F401
from .user import User  # noqa: E402,F401
