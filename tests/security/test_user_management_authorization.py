from tests.conftest import sign_in


def test_user_management_denies_signed_out_and_non_admin_without_disclosure(client, csrf):
    response = client.get("/admin/users/99999")
    assert response.status_code == 401
    assert "99999" not in response.text
    sign_in(client, csrf)
    response = client.get("/admin/users/99999")
    assert response.status_code == 403
    assert "99999" not in response.text


def test_membership_rejects_bad_csrf(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    user = db.query(__import__("auth_entry_portal.models", fromlist=["User"]).User).filter_by(email="member@example.test").one()
    response = client.post(f"/admin/users/{user.id}/memberships", data={"csrf": "bad", "expected_revision": user.revision})
    assert response.status_code == 400
