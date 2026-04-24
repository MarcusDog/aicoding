from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db


app = create_app()

with app.app_context():
    db.create_all()
    print("database initialized")
