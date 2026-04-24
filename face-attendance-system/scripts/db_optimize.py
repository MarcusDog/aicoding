import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text  # noqa: E402

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402


INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_user_name ON user(name)",
    "CREATE INDEX IF NOT EXISTS idx_user_department_status ON user(department, status)",
    "CREATE INDEX IF NOT EXISTS idx_attendance_user_time ON attendance_record(user_id, check_time)",
    "CREATE INDEX IF NOT EXISTS idx_attendance_rule_time ON attendance_record(rule_id, check_time)",
    "CREATE INDEX IF NOT EXISTS idx_attendance_status_time ON attendance_record(status, check_time)",
    "CREATE INDEX IF NOT EXISTS idx_check_rule_active ON check_rule(is_active)",
    "CREATE INDEX IF NOT EXISTS idx_check_rule_admin_active ON check_rule(admin_id, is_active)",
    "CREATE INDEX IF NOT EXISTS idx_operation_created ON operation_log(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_operation_operator ON operation_log(operator_type, operator_id)",
]


def main():
    app = create_app("development")
    with app.app_context():
        for sql in INDEX_SQL:
            try:
                db.session.execute(text(sql))
                db.session.commit()
            except Exception:
                db.session.rollback()
        print("database indexes ensured")


if __name__ == "__main__":
    main()
