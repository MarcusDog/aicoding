from ..extensions import db
from . import TimestampMixin


class Admin(TimestampMixin, db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default="normal", nullable=False)

    check_rules = db.relationship("CheckRule", back_populates="admin", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
