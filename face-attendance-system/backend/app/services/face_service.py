from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from flask import current_app

from ..core.face_detector import FaceDetector
from ..core.liveness_detect import LivenessDetector
from ..core.face_recognizer import FaceRecognizer
from ..core.face_utils import (
    base64_to_image,
    check_image_quality,
    deserialize_embedding,
    serialize_embedding,
)
from ..extensions import db
from ..models import FaceData, User


class FaceService:
    detector = FaceDetector()
    liveness_detector = LivenessDetector()
    _recognizer: FaceRecognizer | None = None
    _embedding_cache: dict[tuple[int, str], np.ndarray] = {}

    @classmethod
    def _get_recognizer(cls) -> FaceRecognizer:
        if cls._recognizer is None:
            cls._recognizer = FaceRecognizer(
                threshold=float(current_app.config.get("FACE_MATCH_THRESHOLD", 0.95)),
                backend=current_app.config.get("FACE_RECOGNIZER_BACKEND", "facenet"),
                projection_path=current_app.config.get("FACE_PROJECTION_PATH"),
                threshold_path=current_app.config.get("FACE_THRESHOLD_PATH"),
            )
        return cls._recognizer

    @classmethod
    def _save_image(cls, image, directory: Path) -> str:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}.jpg"
        path = directory / filename
        if not cv2.imwrite(str(path), image):
            raise ValueError("failed to save image")
        return str(path)

    @classmethod
    def _extract_embedding(cls, image_base64: str):
        image = base64_to_image(image_base64)
        quality = check_image_quality(
            image,
            min_brightness=float(current_app.config.get("MIN_FACE_BRIGHTNESS", 40)),
            min_blur_score=float(current_app.config.get("MIN_FACE_BLUR_SCORE", 30)),
        )
        if not quality["is_valid"]:
            raise ValueError(
                "image quality is too low: "
                f"brightness={quality['brightness']:.1f}, blur={quality['blur_score']:.1f}"
            )

        faces = cls.detector.detect(image)
        if len(faces) != 1:
            raise ValueError("exactly one face is required")

        face = cls.detector.align_face(image=image, box=faces[0]["box"])
        embedding = cls._get_recognizer().extract_embedding(face)
        return image, embedding, quality

    @classmethod
    def _load_known_embedding(cls, face_data: FaceData) -> np.ndarray:
        updated_mark = face_data.updated_at.isoformat() if face_data.updated_at else "none"
        cache_key = (face_data.id, updated_mark)
        cached = cls._embedding_cache.get(cache_key)
        if cached is not None:
            return cached

        embedding = deserialize_embedding(face_data.face_encoding)
        cls._embedding_cache = {cache_key: embedding}
        return embedding

    @classmethod
    def register_or_update_face(cls, user: User, image_base64: str, image_dir: Path) -> FaceData:
        image, embedding, quality = cls._extract_embedding(image_base64)
        image_path = cls._save_image(image, image_dir)

        face_data = FaceData.query.filter_by(user_id=user.id).first()
        if face_data is None:
            face_data = FaceData(user_id=user.id)
            db.session.add(face_data)

        face_data.face_encoding = serialize_embedding(embedding)
        face_data.face_image_path = image_path
        face_data.quality_score = quality["quality_score"]

        user.is_face_registered = True
        db.session.commit()
        cls._embedding_cache.clear()
        return face_data

    @classmethod
    def verify_for_user(cls, user: User, image_base64: str) -> dict:
        if not user.face_data:
            raise ValueError("face data not registered")

        _, current_embedding, _ = cls._extract_embedding(image_base64)
        known_embedding = cls._load_known_embedding(user.face_data)
        recognizer = cls._get_recognizer()
        distance = recognizer.compare(current_embedding, known_embedding)
        threshold = recognizer.threshold
        matched = distance < threshold
        score = max(0.0, min(1.0, 1.0 - distance / max(threshold, 1e-6)))
        return {
            "matched": matched,
            "distance": distance,
            "score": score,
            "threshold": threshold,
        }

    @classmethod
    def get_liveness_action(cls) -> str:
        return cls.liveness_detector.get_action_command()

    @classmethod
    def verify_liveness(cls, frames_base64: list[str], action: str) -> dict:
        if action not in {"blink", "open_mouth"}:
            raise ValueError("invalid liveness action")
        if not frames_base64:
            raise ValueError("frames_base64 is required")

        frames = []
        for frame_data in frames_base64:
            try:
                frames.append(base64_to_image(frame_data))
            except Exception:
                continue

        if not frames:
            raise ValueError("invalid liveness frames")

        passed = cls.liveness_detector.verify_liveness(frames, action)
        return {
            "passed": passed,
            "action": action,
            "frame_count": len(frames),
        }
