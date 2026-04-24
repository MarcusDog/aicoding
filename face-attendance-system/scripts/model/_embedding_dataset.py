from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.face_detector import FaceDetector  # noqa: E402
from app.core.face_recognizer import FaceRecognizer  # noqa: E402


@dataclass
class EmbeddingSample:
    path: Path
    label: str
    embedding: np.ndarray


def iter_images(dataset_dir: Path):
    for person_dir in sorted(dataset_dir.iterdir()):
        if not person_dir.is_dir():
            continue
        label = person_dir.name
        for image_path in person_dir.glob("*"):
            if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            yield image_path, label


def build_embeddings(
    dataset_dir: Path,
    backend: str = "facenet",
    max_per_class: int = 30,
) -> list[EmbeddingSample]:
    detector = FaceDetector()
    recognizer = FaceRecognizer(backend=backend, threshold=0.95)

    samples: list[EmbeddingSample] = []
    per_class_count: dict[str, int] = {}

    for image_path, label in iter_images(dataset_dir):
        count = per_class_count.get(label, 0)
        if count >= max_per_class:
            continue

        image = cv2.imread(str(image_path))
        if image is None:
            continue

        faces = detector.detect(image)
        if len(faces) >= 1:
            face = detector.align_face(image, box=faces[0]["box"])
        else:
            # LFW images are already tightly cropped around faces.
            face = cv2.resize(image, (160, 160))
        embedding = recognizer.extract_embedding(face)
        samples.append(EmbeddingSample(path=image_path, label=label, embedding=embedding))
        per_class_count[label] = count + 1

    return samples
