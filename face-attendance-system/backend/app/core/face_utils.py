import base64
import io

import cv2
import numpy as np


def base64_to_image(base64_str: str) -> np.ndarray:
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    raw = base64.b64decode(base64_str)
    arr = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("invalid image data")
    return image


def image_to_base64(image: np.ndarray) -> str:
    ok, buffer = cv2.imencode(".jpg", image)
    if not ok:
        raise ValueError("failed to encode image")
    return base64.b64encode(buffer.tobytes()).decode("utf-8")


def check_image_quality(
    image: np.ndarray,
    min_brightness: float = 40,
    min_blur_score: float = 25,
) -> dict:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness_ok = brightness >= min_brightness
    blur_ok = blur_score >= min_blur_score
    is_valid = brightness_ok and blur_ok
    quality_score = min(100.0, (brightness / max(min_brightness, 1)) * 40 + (blur_score / max(min_blur_score, 1)) * 60)
    return {
        "brightness": brightness,
        "blur_score": blur_score,
        "brightness_ok": brightness_ok,
        "blur_ok": blur_ok,
        "quality_score": round(quality_score, 2),
        "is_valid": is_valid,
    }


def resize_and_pad(image: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    target_w, target_h = target_size
    h, w = image.shape[:2]
    scale = min(target_w / w, target_h / h)
    resized = cv2.resize(image, (int(w * scale), int(h * scale)))

    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    y_offset = (target_h - resized.shape[0]) // 2
    x_offset = (target_w - resized.shape[1]) // 2
    canvas[y_offset : y_offset + resized.shape[0], x_offset : x_offset + resized.shape[1]] = resized
    return canvas


def serialize_embedding(embedding: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, embedding.astype(np.float32))
    return buffer.getvalue()


def deserialize_embedding(data: bytes) -> np.ndarray:
    buffer = io.BytesIO(data)
    return np.load(buffer)
