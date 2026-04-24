from ..extensions import db
from . import TimestampMixin


class AttendanceRecord(TimestampMixin, db.Model):
    __tablename__ = "attendance_record"
    __table_args__ = (
        db.Index("idx_attendance_user_time", "user_id", "check_time"),
        db.Index("idx_attendance_rule_time", "rule_id", "check_time"),
        db.Index("idx_attendance_status_time", "status", "check_time"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey("check_rule.id"), nullable=False)
    check_time = db.Column(db.DateTime, nullable=False)
    check_type = db.Column(db.String(10), default="in", nullable=False)
    status = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    face_match_score = db.Column(db.Float)
    face_snapshot_path = db.Column(db.String(256))
    device_info = db.Column(db.String(256))
    remark = db.Column(db.String(255))

    user = db.relationship("User", back_populates="attendance_records")
    rule = db.relationship("CheckRule", back_populates="attendance_records")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "rule_id": self.rule_id,
            "check_time": self.check_time.isoformat() if self.check_time else None,
            "check_type": self.check_type,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "face_match_score": self.face_match_score,
            "face_snapshot_path": self.face_snapshot_path,
            "device_info": self.device_info,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
