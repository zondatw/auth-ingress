from __future__ import annotations

from sqlalchemy.orm import Session

from auth_portal.models import AuditEvent

ALLOWED_CONTEXT_KEYS = {"correlation_id", "client_category"}


def sanitized_context(context: dict | None) -> dict:
    return {key: str(value)[:120] for key, value in (context or {}).items() if key in ALLOWED_CONTEXT_KEYS}


def record_event(
    db: Session,
    event_type: str,
    decision: str,
    reason: str,
    *,
    actor_user_id: int | None = None,
    service_entry_id: int | None = None,
    context: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type,
        decision=decision,
        reason=reason[:80],
        actor_user_id=actor_user_id,
        service_entry_id=service_entry_id,
        request_context=sanitized_context(context),
    )
    db.add(event)
    db.commit()
    return event

