def test_liveness_command(client, user_token):
    response = client.get(
        "/api/face/liveness-command",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    action = response.get_json()["data"]["action"]
    assert action in {"blink", "open_mouth"}


def test_admin_faces_endpoint(client, admin_token):
    response = client.get(
        "/api/admin/faces?page=1&size=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert "items" in data
    assert "total" in data


def test_admin_logs_endpoint(client, admin_token):
    response = client.get(
        "/api/admin/logs?page=1&size=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert isinstance(data["items"], list)
