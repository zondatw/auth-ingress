from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from starlette.websockets import WebSocketDisconnect

from auth_ingress.models import AccessRule, PortalSession, ServiceEntry
from tests.conftest import launch_proxy


def test_websocket_without_proxy_credential_is_denied(client, proxy_service):
    with pytest.raises(WebSocketDisconnect) as denied:
        with client.websocket_connect("ws://demo.apps.test/ws"):
            pass
    assert denied.value.code == 1008


def test_websocket_disabled_service_is_denied(client, csrf, proxy_service, db_factory):
    launch_proxy(client, csrf)
    with db_factory() as db:
        service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == "demo"))
        service.websocket_enabled = False
        db.commit()
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("ws://demo.apps.test/ws"):
            pass


def test_expired_session_and_removed_permission_deny_reconnect(client, csrf, proxy_service, db_factory):
    launch_proxy(client, csrf)
    with client.websocket_connect("ws://demo.apps.test/ws") as websocket:
        websocket.send_text("authorized")
        assert websocket.receive_text() == "authorized"
    with db_factory() as db:
        session = db.scalar(select(PortalSession))
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("ws://demo.apps.test/ws"):
            pass

    # A fresh login cannot restore access after the service rule is removed.
    client.cookies.clear()
    launch_proxy(client, csrf)
    with db_factory() as db:
        service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == "demo"))
        db.query(AccessRule).filter(AccessRule.service_entry_id == service.id).delete()
        db.commit()
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("ws://demo.apps.test/ws"):
            pass
