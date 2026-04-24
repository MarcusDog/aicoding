from ..extensions import db
from . import TimestampMixin


class CheckRule(TimestampMixin, db.Model):
    __tablename__ = "check_rule"
    __table_args__ = (
        db.Index("idx_check_rule_active", "is_active"),
        db.Index("idx_check_rule_admin_active", "admin_id", "is_active"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Integer, default=200, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    late_time = db.Column(db.Time)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    week_days = db.Column(db.String(20), default="1,2,3,4,5", nullable=False)

    admin = db.relationship("Admin", back_populates="check_rules")
    attendance_records = db.relationship("AttendanceRecord", back_populates="rule", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "admin_id": self.admin_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "late_time": self.late_time.isoformat() if self.late_time else None,
            "is_active": self.is_active,
            "week_days": self.week_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
