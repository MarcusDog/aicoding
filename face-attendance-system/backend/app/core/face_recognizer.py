from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np


class FaceRecognizer:
    """
    Face embedding extractor with optional post-projection calibration.

    Backends:
    - facenet: facenet-pytorch InceptionResnetV1
    - fallback: handcrafted lightweight descriptor (for dev-only environments)
    """

    def __init__(
        self,
        model_path: str | None = None,
        threshold: float = 0.95,
        backend: str = "facenet",
        projection_path: str | None = None,
        threshold_path: str | None = None,
    ):
        self.threshold = threshold
        self.backend = backend
        self._model = None
        self._torch = None
        self._projection_matrix: np.ndarray | None = None
        self._projection_bias: np.ndarray | None = None
        self._input_size = (160, 160)

        self._load_projection(projection_path)
        self._load_threshold(threshold_path)
        self._init_backend(model_path=model_path)

    def _init_backend(self, model_path: str | None = None):
        if self.backend != "facenet":
            self.backend = "fallback"
            return

        try:
            import torch
            from facenet_pytorch import InceptionResnetV1

            self._torch = torch
            self._model = InceptionResnetV1(pretrained="vggface2").eval()
            if model_path and Path(model_path).exists():
                state_dict = torch.load(model_path, map_location="cpu")
                self._model.load_state_dict(state_dict, strict=False)
        except Exception:
            self.backend = "fallback"

    def _load_projection(self, projection_path: str | None):
        if not projection_path:
            return
        path = Path(projection_path)
        if not path.exists():
            return
        try:
            data = np.load(path)
            self._projection_matrix = data["matrix"].astype(np.float32)
            self._projection_bias = data.get("bias")
            if self._projection_bias is not None:
                self._projection_bias = self._projection_bias.astype(np.float32)
        except Exception:
            self._projection_matrix = None
            self._projection_bias = None

    def _load_threshold(self, threshold_path: str | None):
        if not threshold_path:
            return
        path = Path(threshold_path)
        if not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            value = payload.get("recommended_threshold")
            if isinstance(value, (float, int)):
                self.threshold = float(value)
        except Exception:
            return

    def _normalize(self, embedding: np.ndarray) -> np.ndarray:
        return embedding / (np.linalg.norm(embedding) + 1e-8)

    def _apply_projection(self, embedding: np.ndarray) -> np.ndarray:
        if self._projection_matrix is None:
            return self._normalize(embedding)
        projected = embedding @ self._projection_matrix
        if self._projection_bias is not None:
            projected = projected + self._projection_bias
        return self._normalize(projected.astype(np.float32))

    def _extract_with_facenet(self, face_image: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, self._input_size)
        tensor = self._torch.from_numpy(resized).float().permute(2, 0, 1).unsqueeze(0) / 255.0
        with self._torch.no_grad():
            emb = self._model(tensor).squeeze(0).cpu().numpy().astype(np.float32)
        emb = emb[:128]
        return self._normalize(emb)

    def _extract_with_fallback(self, face_image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (16, 8)).astype(np.float32).flatten()
        emb = resized / 255.0
        return self._normalize(emb)

    def extract_embedding(self, face_image: np.ndarray) -> np.ndarray:
        # TTA: original + horizontal-flip average.
        if self.backend == "facenet" and self._model is not None and self._torch is not None:
            emb1 = self._extract_with_facenet(face_image)
            emb2 = self._extract_with_facenet(cv2.flip(face_image, 1))
            base = self._normalize((emb1 + emb2) / 2.0)
            return self._apply_projection(base)

        base = self._extract_with_fallback(face_image)
        return self._apply_projection(base)

    def compare(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        return float(np.linalg.norm(embedding1 - embedding2))

    def identify(self, face_embedding: np.ndarray, known_embeddings: dict) -> Tuple[str | None, float]:
        best_user = None
        best_distance = float("inf")

        for user_id, emb in known_embeddings.items():
            distance = self.compare(face_embedding, emb)
            if distance < best_distance:
                best_user = str(user_id)
                best_distance = distance

        return best_user, best_distance

    def register_face(self, user_id: int, face_image: np.ndarray) -> np.ndarray:
        return self.extract_embedding(face_image)
