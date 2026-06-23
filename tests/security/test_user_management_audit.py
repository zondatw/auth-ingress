from sqlalchemy import select

from auth_entry_portal.models import AuditEvent
from auth_entry_portal.services.audit_service import record_event


def test_management_audit_is_allowlisted_and_caller_can_commit(db):
    event = record_event(
        db,
        "membership_changed",
        "changed",
        "updated",
        actor_user_id=1,
        target_user_id=2,
        change_summary={"revision": 2, "group_ids": [1], "password": "secret"},
        context={"client_category": "browser", "cookie": "secret"},
        commit=False,
    )
    assert db.scalar(select(AuditEvent).where(AuditEvent.id == event.id)) is event
    assert event.change_summary == {"revision": 2, "group_ids": [1]}
    assert event.request_context == {"client_category": "browser"}
    db.rollback()
    assert db.scalar(select(AuditEvent).where(AuditEvent.event_type == "membership_changed")) is None
