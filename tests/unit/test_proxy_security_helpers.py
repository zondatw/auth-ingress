from datetime import datetime, timedelta, timezone

import pytest

from auth_ingress.config import Settings
from auth_ingress.security.cookies import decode_proxy_credential, encode_proxy_credential
from auth_ingress.security.proxy_destination import UnsafeDestination, join_destination, resolve_destination, websocket_destination
from auth_ingress.security.proxy_host import service_origin, service_slug_from_host
from auth_ingress.services.proxy_authorization_service import ticket_digest
from auth_ingress.services.proxy_header_policy import UnsafeRedirect, filter_cookie_header, filter_request_headers, rewrite_location, rewrite_set_cookie


def test_host_origin_and_path_helpers():
    settings = Settings(proxy_base_domain="apps.test:8443", proxy_scheme="https")
    assert service_slug_from_host("reports.apps.test:8443", settings) == "reports"
    assert service_slug_from_host("reports.apps.test:443", settings) is None
    assert service_origin("reports", settings) == "https://reports.apps.test:8443"
    assert join_destination("http://127.0.0.1:9000/base", "/nested/page", b"x=1&x=2") == "http://127.0.0.1:9000/base/nested/page?x=1&x=2"
    assert websocket_destination("https://127.0.0.1/base", "/ws") == "wss://127.0.0.1/base/ws"


def test_destination_resolution_requires_every_address_to_be_trusted():
    settings = Settings(trusted_downstream_networks=("10.0.0.0/8",))

    def mixed(*args, **kwargs):
        return [(2, 1, 6, "", ("10.1.2.3", 80)), (2, 1, 6, "", ("8.8.8.8", 80))]

    with pytest.raises(UnsafeDestination):
        resolve_destination("http://service.internal", settings, resolver=mixed)


def test_cookie_header_and_set_cookie_policy():
    settings = Settings(session_cookie="portal", proxy_cookie_name="service_proxy")
    assert filter_cookie_header("portal=secret; service_proxy=signed; app=state", settings) == "app=state"
    assert rewrite_set_cookie("app=state; Domain=internal.local; Path=/; HttpOnly", settings) == "app=state; Path=/; HttpOnly"
    assert rewrite_set_cookie("service_proxy=forged; Path=/", settings) is None


def test_hop_headers_and_forwarded_credentials_are_removed():
    settings = Settings(session_cookie="portal", proxy_cookie_name="service_proxy", proxy_scheme="https")
    result = filter_request_headers(
        [(b"connection", b"x-private"), (b"x-private", b"remove"), (b"authorization", b"secret"), (b"cookie", b"portal=x; app=y")],
        settings,
        "127.0.0.1:9000",
        "correlation",
    )
    decoded = [(name.decode(), value.decode()) for name, value in result]
    assert ("cookie", "app=y") in decoded
    assert not any(name in {"authorization", "connection", "x-private"} for name, _ in decoded)
    assert ("host", "127.0.0.1:9000") in decoded


def test_redirect_and_proxy_credential_boundaries():
    assert rewrite_location("http://127.0.0.1:9000/path?q=1", "http://127.0.0.1:9000", "https://demo.apps.test") == "https://demo.apps.test/path?q=1"
    with pytest.raises(UnsafeRedirect):
        rewrite_location("https://public.example/path", "http://127.0.0.1:9000", "https://demo.apps.test")
    settings = Settings(secret_key="test-secret")
    expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
    token = encode_proxy_credential("session", 7, expiry, settings)
    assert decode_proxy_credential(token, settings) == ("session", 7)
    assert decode_proxy_credential(token + "tampered", settings) is None
    assert ticket_digest("ticket", settings) != ticket_digest("other", settings)
