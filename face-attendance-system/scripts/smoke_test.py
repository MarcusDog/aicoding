import argparse

import requests


def assert_ok(resp, label):
    if resp.status_code >= 400:
        raise RuntimeError(f"{label} failed: {resp.status_code} {resp.text}")
    body = resp.json()
    if body.get("success") is False:
        raise RuntimeError(f"{label} failed: {body}")
    return body


def main():
    parser = argparse.ArgumentParser(description="Simple API smoke test.")
    parser.add_argument("--base-url", default="http://localhost:5000/api")
    parser.add_argument("--admin-user", default="admin")
    parser.add_argument("--admin-password", default="admin123")
    args = parser.parse_args()

    login_resp = requests.post(
        f"{args.base_url}/auth/admin-login",
        json={"username": args.admin_user, "password": args.admin_password},
        timeout=10,
    )
    login_body = assert_ok(login_resp, "admin-login")
    token = login_body["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    dashboard_resp = requests.get(f"{args.base_url}/admin/dashboard", headers=headers, timeout=10)
    dashboard_body = assert_ok(dashboard_resp, "dashboard")

    users_resp = requests.get(f"{args.base_url}/admin/users?page=1&size=5", headers=headers, timeout=10)
    users_body = assert_ok(users_resp, "users")
    print(
        "smoke test passed:",
        f"users_total={users_body['data']['total']}",
        f"today={dashboard_body['data'].get('today', {})}",
    )


if __name__ == "__main__":
    main()
