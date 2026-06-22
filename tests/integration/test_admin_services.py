from sqlalchemy import select

from auth_portal.models import AuditEvent, ServiceEntry
from tests.conftest import sign_in


def payload(csrf, **overrides):
    values = {"slug": "reports", "display_name": "Reports", "description": "Internal", "destination": "mock://reports", "status": "enabled", "group_names": "staff", "csrf": csrf}
    values.update(overrides)
    return values


def test_create_changes_visibility_and_is_audited(client, csrf, db_factory):
    sign_in(client, csrf, email="admin@example.test")
    assert client.post("/admin/services", data=payload(csrf)).status_code == 201
    client.post("/sign-out", data={"csrf": csrf})
    sign_in(client, csrf, email="member@example.test")
    assert "Reports" in client.get("/").text
    assert client.get("/services/reports").status_code == 200
    with db_factory() as db:
        assert db.scalar(select(AuditEvent).where(AuditEvent.event_type == "service_entry_created"))


def test_update_and_disable_take_effect(client, csrf):
    sign_in(client, csrf, email="admin@example.test")
    client.post("/admin/services", data=payload(csrf))
    response = client.post("/admin/services/reports", data=payload(csrf, display_name="New Reports", status="disabled", group_names=""))
    assert response.status_code == 200
    client.post("/sign-out", data={"csrf": csrf})
    sign_in(client, csrf)
    assert "New Reports" not in client.get("/").text
    assert client.get("/services/reports").status_code == 503


def test_audit_review_is_redacted(client, csrf):
    sign_in(client, csrf, email="admin@example.test")
    client.post("/admin/services", data=payload(csrf))
    response = client.get("/admin/audit")
    assert "service_entry_created" in response.text
    assert "correct-password" not in response.text


def test_existing_service_form_prefills_assigned_groups(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    response = client.get("/admin/services")

    assert response.status_code == 200
    demo_form = response.text.split('action="/admin/services/demo"', 1)[1].split("</form>", 1)[0]
    assert 'name="group_names" value="staff"' in demo_form
