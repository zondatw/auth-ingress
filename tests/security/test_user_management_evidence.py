from sqlalchemy import select

from auth_entry_portal.models import AuditEvent, User
from auth_entry_portal.services.audit_service import record_event


def test_management_evidence_has_actor_target_outcome_and_no_secrets(db):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    target = db.query(User).filter_by(email="member@example.test").one()
    event = record_event(
        db,
        "user_updated",
        "changed",
        "profile_updated",
        actor_user_id=actor.id,
        target_user_id=target.id,
        context={"client_category": "browser", "cookie": "cookie-secret"},
        change_summary={"revision": 4, "field_names": ["display_name"], "token": "reset-secret", "password": "password-secret"},
    )
    stored = db.scalar(select(AuditEvent).where(AuditEvent.id == event.id))
    serialized = f"{stored.request_context}{stored.change_summary}".casefold()
    assert stored.actor_user_id == actor.id and stored.target_user_id == target.id
    assert stored.decision == "changed" and stored.reason == "profile_updated"
    assert all(secret not in serialized for secret in ("cookie-secret", "reset-secret", "password-secret"))
