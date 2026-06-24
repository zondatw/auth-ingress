from tests.conftest import sign_in


def test_non_admin_management_denial_is_not_rendered_as_field_validation(client, csrf):
    sign_in(client, csrf, email="member@example.test")

    response = client.get("/admin/users")

    assert response.status_code == 403
    assert "field-error" not in response.text
    assert "Administrator access required" in response.text


def test_stale_user_update_conflict_is_page_level_not_field_validation(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    user = db.query(__import__("auth_ingress.models", fromlist=["User"]).User).filter_by(email="member@example.test").one()

    response = client.post(
        f"/admin/users/{user.id}/profile",
        data={
            "csrf": csrf,
            "expected_revision": user.revision + 100,
            "email": "member2@example.test",
            "display_name": "Member Two",
        },
    )

    assert response.status_code == 409
    assert "User changed; refresh and preview again" in response.text
    assert "field-error" not in response.text
