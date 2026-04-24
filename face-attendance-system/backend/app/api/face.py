from flask import Blueprint, current_app, request

from ..services.face_service import FaceService
from ..utils.decorators import get_current_user, user_required
from ..utils.response import success_response
from ..utils.validators import require_fields

face_bp = Blueprint("face", __name__, url_prefix="/face")


@face_bp.get("/status")
@user_required
def face_status():
    user = get_current_user()
    face_data = user.face_data.to_dict() if user.face_data else None
    return success_response(
        {
            "is_face_registered": user.is_face_registered,
            "face_data": face_data,
        }
    )


@face_bp.post("/register")
@user_required
def register_face():
    payload = request.get_json() or {}
    require_fields(payload, ["image_base64"])

    if payload.get("action") and payload.get("frames_base64"):
        liveness_result = FaceService.verify_liveness(payload["frames_base64"], payload["action"])
        if not liveness_result["passed"]:
            raise ValueError("liveness verification failed")

    user = get_current_user()
    face_data = FaceService.register_or_update_face(
        user=user,
        image_base64=payload["image_base64"],
        image_dir=current_app.config["FACE_IMAGE_DIR"],
    )
    return success_response(face_data.to_dict(), message="face registered")


@face_bp.put("/update")
@user_required
def update_face():
    payload = request.get_json() or {}
    require_fields(payload, ["image_base64"])

    user = get_current_user()
    face_data = FaceService.register_or_update_face(
        user=user,
        image_base64=payload["image_base64"],
        image_dir=current_app.config["FACE_IMAGE_DIR"],
    )
    return success_response(face_data.to_dict(), message="face updated")


@face_bp.post("/verify")
@user_required
def verify_face():
    payload = request.get_json() or {}
    require_fields(payload, ["image_base64"])

    user = get_current_user()
    result = FaceService.verify_for_user(user, payload["image_base64"])
    return success_response(result)


@face_bp.get("/liveness-command")
@user_required
def liveness_command():
    return success_response({"action": FaceService.get_liveness_action()})


@face_bp.post("/liveness-verify")
@user_required
def liveness_verify():
    payload = request.get_json() or {}
    require_fields(payload, ["action", "frames_base64"])
    if not isinstance(payload["frames_base64"], list):
        raise ValueError("frames_base64 must be an array")

    result = FaceService.verify_liveness(
        frames_base64=payload["frames_base64"],
        action=payload["action"],
    )
    return success_response(result)
