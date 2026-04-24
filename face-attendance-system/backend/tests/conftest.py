import pytest

from app import create_app
from app.extensions import db
from app.models import Admin
from app.services.auth_service import AuthService


@pytest.fixture()
def app():
    app = create_app("testing")
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        RATE_LIMIT_STORAGE_URI="memory://",
    )

    with app.app_context():
        db.create_all()
        admin = Admin(
            username="admin",
            password_hash=AuthService.hash_password("123456"),
            real_name="System Admin",
            role="super",
        )
        db.session.add(admin)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_token(client):
    response = client.post(
        "/api/auth/admin-login",
        json={"username": "admin", "password": "123456"},
    )
    assert response.status_code == 200
    body = response.get_json()
    return body["data"]["token"]


@pytest.fixture()
def user_token(client):
    response = client.post(
        "/api/auth/wx-login",
        json={"code": "pytest-code-001", "name": "pytest-user"},
    )
    assert response.status_code == 200
    body = response.get_json()
    return body["data"]["token"]
