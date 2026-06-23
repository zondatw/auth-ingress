from tests.conftest import sign_in


def test_admin_lifecycle_controls_are_visible(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    models = __import__("auth_entry_portal.models", fromlist=["User"])
    target = db.query(models.User).filter_by(email="member@example.test").one()
    page = client.get(f"/admin/users/{target.id}")
    assert "disable account" in page.text.casefold()
    assert "password reset" in page.text.casefold()
    assert "Update profile" in page.text
