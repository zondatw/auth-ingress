from tests.conftest import sign_in


def test_browser_visible_identity_uses_auth_ingress(client, csrf):
    sign_in_page = client.get("/sign-in")
    assert "auth-ingress" in sign_in_page.text
    sign_in(client, csrf, email="admin@example.test")
    for path in ("/", "/admin/users", "/admin/services", "/admin/audit"):
        response = client.get(path)
        assert response.status_code == 200
        assert "auth-ingress" in response.text
        assert "Auth Portal" not in response.text

