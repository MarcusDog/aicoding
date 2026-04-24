from __future__ import annotations

import random
from typing import List

import cv2
import numpy as np


class LivenessDetector:
    """
    Lightweight liveness estimator based on temporal facial-region dynamics.

    This is not a production anti-spoofing model, but it is stronger than static
    single-frame checks and fits low-cost graduation-project deployments.
    """

    def __init__(self):
        self.actions = ["blink", "open_mouth"]
        self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def get_action_command(self) -> str:
        return random.choice(self.actions)

    def _crop_face(self, frame: np.ndarray) -> np.ndarray | None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) == 0:
            return None
        x, y, w, h = max(faces, key=lambda item: item[2] * item[3])
        return gray[y : y + h, x : x + w]

    @staticmethod
    def _eye_ratio(face_gray: np.ndarray) -> float:
        h, w = face_gray.shape[:2]
        eye_region = face_gray[int(0.15 * h) : int(0.42 * h), :]
        left_eye = eye_region[:, : w // 2]
        right_eye = eye_region[:, w // 2 :]
        if left_eye.size == 0 or right_eye.size == 0:
            return 0.0
        left_contrast = float(np.std(left_eye))
        right_contrast = float(np.std(right_eye))
        return (left_contrast + right_contrast) / 2.0

    @staticmethod
    def _mouth_ratio(face_gray: np.ndarray) -> float:
        h, w = face_gray.shape[:2]
        mouth = face_gray[int(0.62 * h) : int(0.9 * h), int(0.2 * w) : int(0.8 * w)]
        if mouth.size == 0:
            return 0.0
        # Dark pixel ratio approximates open mouth cavity signal.
        dark_ratio = float(np.mean(mouth < 70))
        texture = float(np.std(mouth) / 255.0)
        return dark_ratio * 0.7 + texture * 0.3

    def check_frame(self, frame: np.ndarray, action: str) -> dict:
        face = self._crop_face(frame)
        if face is None:
            return {"passed": False, "ear": 0.0, "mar": 0.0, "face_detected": False}

        ear_like = self._eye_ratio(face) / 40.0
        mar_like = self._mouth_ratio(face)
        passed = ear_like > 0.18 if action == "blink" else mar_like > 0.22
        return {
            "passed": bool(passed),
            "ear": round(float(ear_like), 4),
            "mar": round(float(mar_like), 4),
            "face_detected": True,
        }

    def verify_liveness(self, frames: List[np.ndarray], action: str) -> bool:
        if not frames:
            return False

        ear_values = []
        mar_values = []
        valid_frames = 0
        pass_count = 0

        for frame in frames:
            result = self.check_frame(frame, action)
            if not result["face_detected"]:
                continue
            valid_frames += 1
            ear_values.append(result["ear"])
            mar_values.append(result["mar"])
            if result["passed"]:
                pass_count += 1

        if valid_frames < 3:
            return False

        # Temporal dynamics rule: require enough action frames and noticeable variance.
        ear_var = float(np.var(ear_values)) if ear_values else 0.0
        mar_var = float(np.var(mar_values)) if mar_values else 0.0
        motion_ok = ear_var > 0.0008 if action == "blink" else mar_var > 0.0005
        action_ratio = pass_count / valid_frames
        return bool(action_ratio >= 0.35 and motion_ok)
