import argparse
import random
import sys
from datetime import datetime, time, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import create_app  # noqa: E402
from app.core.face_utils import serialize_embedding  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import Admin, AttendanceRecord, CheckRule, FaceData, User  # noqa: E402


DEPARTMENTS = ["R&D", "Product", "Operations", "HR", "Finance"]
FIRST_NAMES = [
    "Aiden",
    "Bella",
    "Carter",
    "Diana",
    "Ethan",
    "Fiona",
    "Gavin",
    "Hannah",
    "Ivan",
    "Julia",
    "Kevin",
    "Lily",
]


def random_name(seed: int) -> str:
    random.seed(seed)
    return f"{random.choice(FIRST_NAMES)}-{seed:03d}"


def random_face_embedding(person_seed: int) -> bytes:
    rng = np.random.default_rng(person_seed)
    vector = rng.normal(0, 1, 128).astype(np.float32)
    vector = vector / (np.linalg.norm(vector) + 1e-8)
    return serialize_embedding(vector)


def ensure_rule(admin_id: int) -> CheckRule:
    rule = CheckRule.query.filter_by(name="Default Office Rule").first()
    if rule:
        return rule
    rule = CheckRule(
        name="Default Office Rule",
        admin_id=admin_id,
        latitude=31.2304,
        longitude=121.4737,
        radius=250,
        start_time=time(8, 0, 0),
        end_time=time(10, 0, 0),
        late_time=time(8, 30, 0),
        week_days="1,2,3,4,5",
        is_active=True,
    )
    db.session.add(rule)
    db.session.commit()
    return rule


def create_users(count: int, face_ratio: float) -> list[User]:
    users: list[User] = []
    for idx in range(1, count + 1):
        user = User(
            name=random_name(idx),
            employee_no=f"EMP{idx:05d}",
            department=random.choice(DEPARTMENTS),
            phone=f"138{idx:08d}"[:11],
            status=True,
        )
        users.append(user)
    db.session.add_all(users)
    db.session.flush()

    for idx, user in enumerate(users, start=1):
        if random.random() <= face_ratio:
            face_data = FaceData(
                user_id=user.id,
                face_encoding=random_face_embedding(idx),
                face_image_path=f"demo/faces/{user.employee_no}.jpg",
                quality_score=round(random.uniform(70, 95), 2),
            )
            user.is_face_registered = True
            db.session.add(face_data)

    db.session.commit()
    return users


def create_attendance(rule: CheckRule, days: int):
    end_date = datetime.now().replace(hour=8, minute=20, second=0, microsecond=0)
    users = User.query.filter_by(status=True).all()
    records: list[AttendanceRecord] = []

    for day_offset in range(days):
        dt = end_date - timedelta(days=day_offset)
        if dt.weekday() >= 5:
            continue

        for user in users:
            if not user.is_face_registered:
                continue
            # 92% attendance rate for demos
            if random.random() > 0.92:
                continue

            is_late = random.random() < 0.12
            minute = random.randint(35, 55) if is_late else random.randint(2, 28)
            check_time = dt.replace(hour=8, minute=minute)
            records.append(
                AttendanceRecord(
                    user_id=user.id,
                    rule_id=rule.id,
                    check_time=check_time,
                    check_type="in",
                    status="late" if is_late else "normal",
                    latitude=rule.latitude + random.uniform(-0.0005, 0.0005),
                    longitude=rule.longitude + random.uniform(-0.0005, 0.0005),
                    face_match_score=round(random.uniform(0.78, 0.99), 3),
                    face_snapshot_path=f"demo/snapshots/{user.employee_no}_{check_time:%Y%m%d}.jpg",
                    device_info=random.choice(["iPhone 14 Pro", "iPhone 13", "Xiaomi 14", "HUAWEI Mate 60"]),
                )
            )

    db.session.add_all(records)
    db.session.commit()
    return len(records)


def maybe_clear_existing(clear: bool):
    if not clear:
        return
    AttendanceRecord.query.delete()
    FaceData.query.delete()
    User.query.delete()
    CheckRule.query.filter(CheckRule.name == "Default Office Rule").delete()
    db.session.commit()


def main():
    parser = argparse.ArgumentParser(description="Generate reproducible demo data.")
    parser.add_argument("--users", type=int, default=120, help="number of demo users")
    parser.add_argument("--days", type=int, default=45, help="days of attendance history")
    parser.add_argument("--face-ratio", type=float, default=0.85, help="ratio of users with face data")
    parser.add_argument("--clear", action="store_true", help="clear old demo data first")
    args = parser.parse_args()

    app = create_app("development")
    with app.app_context():
        db.create_all()
        admin = Admin.query.first()
        if not admin:
            print("No admin found. Run scripts/init_db.py first.")
            return

        maybe_clear_existing(args.clear)
        users = create_users(count=args.users, face_ratio=max(0.0, min(args.face_ratio, 1.0)))
        rule = ensure_rule(admin.id)
        total_records = create_attendance(rule=rule, days=max(1, args.days))

        print(
            f"demo data ready: users={len(users)}, "
            f"registered_faces={sum(1 for u in users if u.is_face_registered)}, "
            f"attendance_records={total_records}"
        )


if __name__ == "__main__":
    main()
