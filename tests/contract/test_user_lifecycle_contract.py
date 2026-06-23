from auth_entry_portal.main import create_app
from auth_entry_portal.models import User
from tests.conftest import sign_in


def test_lifecycle_and_recovery_routes_are_registered():
    paths = create_app(initialize_schema=False).openapi()["paths"]
    assert "post" in paths["/admin/users/preview"]
    assert "post" in paths["/admin/users/{user_id}/profile"]
    assert "post" in paths["/admin/users/{user_id}/status"]
    assert "post" in paths["/admin/users/{user_id}/reset-password"]
    assert {"get", "post"} <= paths["/reset-password"].keys()
    assert {"get", "post"} <= paths["/change-password"].keys()


def test_create_and_status_forms_preview_before_commit(client, csrf, db_factory, db):
    sign_in(client, csrf, email="admin@example.test")
    preview = client.post("/admin/users/preview", data={"csrf": csrf, "email": "preview@example.test", "display_name": "Preview", "status": "active"})
    assert preview.status_code == 200 and "Preview user creation" in preview.text
    with db_factory() as check:
        assert check.query(User).filter_by(email="preview@example.test").first() is None
    target = db.query(User).filter_by(email="member@example.test").one()
    status_preview = client.post(f"/admin/users/{target.id}/status", data={"csrf": csrf, "expected_revision": target.revision, "status": "disabled"})
    assert status_preview.status_code == 200 and "Confirm status change" in status_preview.text
    with db_factory() as check:
        assert check.get(User, target.id).status == "active"
