from tests.conftest import sign_in


def test_admin_route_contract(client, csrf):
    sign_in(client, csrf, email="admin@example.test")
    assert client.get("/admin/services").status_code == 200
    created = client.post("/admin/services", data={
        "slug": "reports", "display_name": "Reports", "description": "Internal reports",
        "destination": "mock://reports", "status": "enabled", "group_names": "staff", "csrf": csrf,
    })
    assert created.status_code == 201
    updated = client.post("/admin/services/reports", data={
        "slug": "reports", "display_name": "Reports", "description": "",
        "destination": "mock://reports", "status": "disabled", "group_names": "", "csrf": csrf,
    })
    assert updated.status_code == 200
    assert client.get("/admin/audit").status_code == 200


def test_non_admin_contract_is_403(client, csrf):
    sign_in(client, csrf)
    assert client.get("/admin/services").status_code == 403
    assert client.get("/admin/audit").status_code == 403

