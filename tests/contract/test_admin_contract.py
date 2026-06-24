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


def test_invalid_service_create_preserves_safe_values_and_field_error(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    response = client.post(
        "/admin/services",
        data={
            "slug": "bad slug",
            "display_name": "Reports",
            "description": "Internal reports",
            "destination": "mock://reports",
            "status": "enabled",
            "group_names": "staff",
            "proxy_enabled": "true",
            "websocket_enabled": "true",
            "csrf": csrf,
        },
    )

    assert response.status_code == 400
    assert 'name="slug" pattern="[a-z0-9-]+" value="bad slug"' in response.text
    assert 'name="display_name" value="Reports"' in response.text
    assert 'name="description" value="Internal reports"' in response.text
    assert 'name="destination" placeholder="https://app.internal" value="mock://reports"' in response.text
    assert 'name="group_names" value="staff"' in response.text
    assert 'name="proxy_enabled" value="true" checked' in response.text
    assert 'name="websocket_enabled" value="true" checked' in response.text
    assert "Slug must contain lowercase letters, numbers, and hyphens" in response.text


def test_invalid_service_group_preserves_values_and_identifies_group_field(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    response = client.post(
        "/admin/services",
        data={
            "slug": "reports",
            "display_name": "Reports",
            "description": "Internal reports",
            "destination": "mock://reports",
            "status": "enabled",
            "group_names": "missing-group",
            "csrf": csrf,
        },
    )

    assert response.status_code == 400
    assert 'name="group_names" value="missing-group"' in response.text
    assert "One or more groups do not exist" in response.text
