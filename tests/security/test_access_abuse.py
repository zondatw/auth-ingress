from sqlalchemy import select

from auth_entry_portal.models import AuditEvent
from auth_entry_portal.services.audit_service import sanitized_context
from tests.conftest import sign_in


def test_failed_sign_in_is_generic_and_audited(client, csrf, db_factory):
    response = sign_in(client, csrf, email="unknown@example.test", password="secret-value")
    assert response.status_code == 401
    assert "unknown@example.test" not in response.text
    assert "secret-value" not in response.text
    with db_factory() as db:
        event = db.scalar(select(AuditEvent).where(AuditEvent.event_type == "sign_in_failure"))
        assert event.reason == "invalid_credentials"
        assert "secret-value" not in str(event.request_context)


def test_audit_context_is_allowlisted():
    result = sanitized_context({"correlation_id": "abc", "client_category": "browser", "password": "secret", "session_id": "sid"})
    assert result == {"correlation_id": "abc", "client_category": "browser"}


def test_denial_is_audited_before_response(client, csrf, db_factory):
    sign_in(client, csrf, email="outsider@example.test")
    assert client.get("/services/demo").status_code == 403
    with db_factory() as db:
        event = db.scalar(select(AuditEvent).where(AuditEvent.event_type == "service_entry_denied"))
        assert event.decision == "denied"

