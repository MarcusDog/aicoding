def test_admin_login_success(client):
    response = client.post(
        "/api/auth/admin-login",
        json={"username": "admin", "password": "123456"},
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert "token" in data
    assert data["admin"]["username"] == "admin"


def test_profile_with_admin_token(client, admin_token):
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["type"] == "admin"
    assert data["profile"]["username"] == "admin"
