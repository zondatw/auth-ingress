from tests.conftest import sign_in
from tests.ui_style_helpers import assert_forbidden_values_absent


def test_refreshed_pages_do_not_expose_server_secrets(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    for path in ("/", "/admin/users", "/admin/groups", "/admin/services", "/admin/audit", "/reset-password"):
        response = client.get(path)
        assert response.status_code in {200, 303}
        assert_forbidden_values_absent(response.text)


def test_non_admin_cannot_see_admin_summary_cards(client, csrf):
    sign_in(client, csrf)

    response = client.get("/admin/users")

    assert response.status_code == 403
    assert "Active users" not in response.text
    assert "Administrators" not in response.text
    assert "User management summary" not in response.text


def test_temporary_password_only_appears_after_confirmed_user_create(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    list_response = client.get("/admin/users")
    assert "Temporary password" not in list_response.text

    created = client.post(
        "/admin/users/confirm",
        data={
            "email": "new-tech-user@example.test",
            "display_name": "New Tech User",
            "status": "active",
            "csrf": csrf,
        },
    )

    assert created.status_code == 201
    assert "Temporary password" in created.text
    assert "Copy temporary password" in created.text
    assert "must change it after signing in" in created.text


def test_security_sensitive_states_have_non_color_text_cues(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    users = client.get("/admin/users").text
    services = client.get("/admin/services").text

    assert ">active<" in users or "active</span>" in users
    assert ">disabled<" in users or "disabled</span>" in users
    assert ">enabled<" in services or "enabled</span>" in services
    assert "The form expired. Please try again." not in users
