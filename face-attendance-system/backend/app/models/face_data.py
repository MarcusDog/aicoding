from ..extensions import db
from . import TimestampMixin


class FaceData(TimestampMixin, db.Model):
    __tablename__ = "face_data"
    __table_args__ = (db.Index("idx_face_data_updated", "updated_at"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    face_image_path = db.Column(db.String(256))
    quality_score = db.Column(db.Float)

    user = db.relationship("User", back_populates="face_data")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "face_image_path": self.face_image_path,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
