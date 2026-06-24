from sqlalchemy import select

from auth_ingress.models import AuditEvent
from tests.conftest import launch_proxy, sign_in


def test_proxy_logs_and_audits_exclude_sensitive_values(client, csrf, proxy_service, db_factory, caplog):
    origin = launch_proxy(client, csrf)
    secret_body = "body-secret-value"
    secret_query = "query-secret-value"
    secret_filename = "private-name.txt"
    client.post(origin + f"/api/data?private={secret_query}", content=secret_body, headers={"X-Filename": secret_filename})
    client.get(origin + "/redirect/external", follow_redirects=False)
    combined_logs = "\n".join(record.getMessage() for record in caplog.records)
    for value in [secret_body, secret_query, secret_filename, proxy_service, "auth_portal_service"]:
        assert value not in combined_logs
    with db_factory() as db:
        events = list(db.scalars(select(AuditEvent)).all())
        serialized = "\n".join(f"{event.event_type}:{event.reason}:{event.request_context}" for event in events)
    for value in [secret_body, secret_query, secret_filename, proxy_service, "ticket="]:
        assert value not in serialized


def test_invalid_launch_does_not_echo_ticket(client, csrf, proxy_service):
    sign_in(client, csrf)
    secret_ticket = "not-a-real-secret-ticket"
    response = client.get(f"http://demo.apps.test/__portal/bootstrap?ticket={secret_ticket}")
    assert response.status_code == 403
    assert secret_ticket not in response.text
