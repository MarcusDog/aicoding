from __future__ import annotations

from typing import Any

import cv2
import numpy as np


class FaceDetector:
    def __init__(self, min_face_size: int = 40, thresholds: list[float] | None = None):
        self.min_face_size = min_face_size
        self.thresholds = thresholds or [0.6, 0.7, 0.7]
        self._mtcnn = None

        try:
            from facenet_pytorch import MTCNN

            self._mtcnn = MTCNN(keep_all=True, min_face_size=min_face_size)
        except Exception:
            self._cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

    def detect(self, image: np.ndarray) -> list[dict[str, Any]]:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if self._mtcnn is not None:
            boxes, probs = self._mtcnn.detect(rgb)
            detections: list[dict[str, Any]] = []
            if boxes is None:
                return detections
            for box, prob in zip(boxes, probs):
                x1, y1, x2, y2 = [int(max(v, 0)) for v in box]
                detections.append({"box": [x1, y1, x2, y2], "confidence": float(prob), "landmarks": {}})
            return sorted(detections, key=lambda item: item["confidence"], reverse=True)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self._cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        detections = []
        for x, y, w, h in faces:
            detections.append({"box": [int(x), int(y), int(x + w), int(y + h)], "confidence": 0.8, "landmarks": {}})
        return sorted(detections, key=lambda item: item["confidence"], reverse=True)

    def align_face(self, image: np.ndarray, landmarks: dict | None = None, box: list[int] | None = None) -> np.ndarray:
        if box:
            x1, y1, x2, y2 = box
            face = image[y1:y2, x1:x2]
        else:
            face = image
        if face.size == 0:
            raise ValueError("failed to crop face")
        return cv2.resize(face, (160, 160))

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return rgb.astype(np.float32) / 255.0
