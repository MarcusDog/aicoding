from ..extensions import db
from . import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "user"
    __table_args__ = (
        db.Index("idx_user_name", "name"),
        db.Index("idx_user_department_status", "department", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(128), unique=True, index=True)
    name = db.Column(db.String(50), nullable=False)
    employee_no = db.Column(db.String(50), unique=True, index=True)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(256))
    is_face_registered = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.Boolean, default=True, nullable=False)

    face_data = db.relationship("FaceData", back_populates="user", uselist=False)
    attendance_records = db.relationship("AttendanceRecord", back_populates="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "openid": self.openid,
            "name": self.name,
            "employee_no": self.employee_no,
            "department": self.department,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "is_face_registered": self.is_face_registered,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
