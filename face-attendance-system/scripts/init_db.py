import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import Admin  # noqa: E402
from app.services.auth_service import AuthService  # noqa: E402


def main():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            admin = Admin(
                username="admin",
                password_hash=AuthService.hash_password("admin123"),
                real_name="系统管理员",
                role="super",
            )
            db.session.add(admin)
            db.session.commit()
            print("created default admin: admin/admin123")
        else:
            print("admin already exists")

        print("database initialized")


if __name__ == "__main__":
    main()
