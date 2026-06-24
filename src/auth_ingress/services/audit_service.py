from __future__ import annotations

from sqlalchemy.orm import Session

from auth_ingress.models import AuditEvent

ALLOWED_CONTEXT_KEYS = {"correlation_id", "client_category"}
ALLOWED_CHANGE_KEYS = {"revision", "field_names", "group_ids", "groups_added", "groups_removed", "status", "is_admin", "count"}

PROXY_AUDIT_EVENTS = {
    "proxy_launch_created",
    "proxy_launch_consumed",
    "proxy_launch_denied",
    "proxy_request_denied",
    "proxy_websocket_denied",
    "proxy_redirect_denied",
    "proxy_upstream_unavailable",
    "proxy_compatibility_checked",
}


def sanitized_context(context: dict | None) -> dict:
    return {key: str(value)[:120] for key, value in (context or {}).items() if key in ALLOWED_CONTEXT_KEYS}


def sanitized_changes(changes: dict | None) -> dict:
    result: dict = {}
    for key, value in (changes or {}).items():
        if key not in ALLOWED_CHANGE_KEYS:
            continue
        if isinstance(value, list):
            result[key] = [item if isinstance(item, (int, bool)) else str(item)[:120] for item in value[:100]]
        elif isinstance(value, (int, bool)):
            result[key] = value
        else:
            result[key] = str(value)[:120]
    return result


def record_event(
    db: Session,
    event_type: str,
    decision: str,
    reason: str,
    *,
    actor_user_id: int | None = None,
    target_user_id: int | None = None,
    service_entry_id: int | None = None,
    context: dict | None = None,
    change_summary: dict | None = None,
    commit: bool = True,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type,
        decision=decision,
        reason=reason[:80],
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        service_entry_id=service_entry_id,
        request_context=sanitized_context(context),
        change_summary=sanitized_changes(change_summary),
    )
    db.add(event)
    if commit:
        db.commit()
    else:
        db.flush()
    return event
