def test_admin_create_and_list_user(client, admin_token):
    create_resp = client.post(
        "/api/admin/users",
        json={"name": "Alice", "employee_no": "E001", "department": "R&D"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201

    list_resp = client.get(
        "/api/admin/users?page=1&size=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_resp.status_code == 200
    body = list_resp.get_json()["data"]
    assert body["total"] >= 1
    assert any(item["name"] == "Alice" for item in body["items"])
