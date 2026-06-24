from auth_ingress.models import AuditEvent, Group, User
from tests.conftest import sign_in


def test_group_management_denies_non_admin_without_group_data(client, csrf):
    sign_in(client, csrf, email="member@example.test")

    response = client.get("/admin/groups")

    assert response.status_code == 403
    assert "Administrator access required" in response.text
    assert "staff" not in response.text
    assert "admins" not in response.text


def test_group_create_csrf_failure_preserves_safe_values_without_secret_echo(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    response = client.post("/admin/groups", data={"csrf": "bad", "name": "security", "description": "contains no token", "token": "must-not-return"})

    assert response.status_code == 400
    assert "security" in response.text
    assert "must-not-return" not in response.text


def test_group_lifecycle_stale_and_denied_outcomes_make_no_change(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    staff = db.query(Group).filter_by(name="staff").one()

    stale = client.post(
        f"/admin/groups/{staff.id}/lifecycle",
        data={"csrf": csrf, "expected_revision": staff.revision + 100, "action": "deactivate", "confirm": "true"},
    )
    assert stale.status_code == 409
    db.refresh(staff)
    assert staff.status == "active"


def test_group_audit_redacts_sensitive_values_and_records_target_group(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    response = client.post("/admin/groups", data={"csrf": csrf, "name": "audit-group", "description": "Audit"})
    assert response.status_code in {200, 303}
    group = db.query(Group).filter_by(name="audit-group").one()

    event = db.query(AuditEvent).filter_by(target_group_id=group.id, event_type="group_created").one()
    assert event.actor_user_id == db.query(User).filter_by(email="admin@example.test").one().id
    assert "secret" not in str(event.change_summary).casefold()
