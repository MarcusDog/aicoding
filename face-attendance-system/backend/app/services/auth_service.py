import hashlib

import bcrypt
import requests
from flask import current_app, request
from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models import Admin, OperationLog, User


class AuthService:
    @staticmethod
    def _resolve_openid(code: str) -> str:
        mode = current_app.config.get("WECHAT_LOGIN_MODE", "mock")
        if mode != "real":
            return hashlib.sha256(code.encode("utf-8")).hexdigest()[:32]

        appid = current_app.config.get("WECHAT_APPID")
        secret = current_app.config.get("WECHAT_SECRET")
        if not appid or not secret:
            raise ValueError("wechat appid/secret not configured")

        url = "https://api.weixin.qq.com/sns/jscode2session"
        try:
            response = requests.get(
                url,
                params={
                    "appid": appid,
                    "secret": secret,
                    "js_code": code,
                    "grant_type": "authorization_code",
                },
                timeout=8,
            )
            payload = response.json()
        except requests.RequestException as exc:
            raise ValueError("wechat service unavailable") from exc
        openid = payload.get("openid")
        if not openid:
            message = payload.get("errmsg") or "wechat login failed"
            raise ValueError(message)
        return openid

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def admin_login(username: str, password: str) -> tuple[Admin, str]:
        admin = Admin.query.filter_by(username=username).first()
        if not admin or not AuthService.verify_password(password, admin.password_hash):
            raise ValueError("invalid username or password")

        token = create_access_token(
            identity=str(admin.id),
            additional_claims={"type": "admin", "role": admin.role},
        )
        AuthService.log_action(admin.id, "admin", "admin_login", f"username={admin.username}")
        db.session.commit()
        return admin, token

    @staticmethod
    def wx_login(code: str, user_info: dict | None = None) -> tuple[User, str]:
        openid = AuthService._resolve_openid(code)
        user = User.query.filter_by(openid=openid).first()

        if not user:
            suffix = openid[:6]
            user = User(
                openid=openid,
                name=(user_info or {}).get("name") or f"用户{suffix}",
                avatar_url=(user_info or {}).get("avatar_url"),
                department=(user_info or {}).get("department"),
            )
            db.session.add(user)
            db.session.flush()
            AuthService.log_action(user.id, "user", "wx_register", f"openid={openid}")

        token = create_access_token(identity=str(user.id), additional_claims={"type": "user"})
        db.session.commit()
        return user, token

    @staticmethod
    def log_action(operator_id: int | None, operator_type: str, action: str, detail: str | None = None):
        entry = OperationLog(
            operator_id=operator_id,
            operator_type=operator_type,
            action=action,
            detail=detail,
            ip_address=request.remote_addr,
        )
        db.session.add(entry)
