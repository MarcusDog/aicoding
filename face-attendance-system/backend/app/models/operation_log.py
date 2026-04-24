from ..extensions import db
from . import TimestampMixin


class OperationLog(TimestampMixin, db.Model):
    __tablename__ = "operation_log"
    __table_args__ = (
        db.Index("idx_operation_created", "created_at"),
        db.Index("idx_operation_operator", "operator_type", "operator_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer)
    operator_type = db.Column(db.String(20))
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text)
    ip_address = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "operator_id": self.operator_id,
            "operator_type": self.operator_type,
            "action": self.action,
            "detail": self.detail,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
