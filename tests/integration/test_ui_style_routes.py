from tests.conftest import sign_in


def test_refreshed_admin_routes_preserve_successful_responses(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    for path in ("/", "/admin/users", "/admin/groups", "/admin/services", "/admin/audit"):
        response = client.get(path)
        assert response.status_code == 200
        assert "auth-ingress" in response.text


def test_refreshed_auth_routes_preserve_successful_responses(client):
    assert client.get("/sign-in").status_code == 200
    assert client.get("/reset-password").status_code == 200


def test_refreshed_admin_routes_preserve_denial_responses(client, csrf):
    sign_in(client, csrf)

    for path in ("/admin/users", "/admin/groups", "/admin/services", "/admin/audit"):
        response = client.get(path)
        assert response.status_code == 403
        assert "Return to service list" in response.text
