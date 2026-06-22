from datetime import datetime, timedelta, timezone

import pytest

from auth_entry_portal.config import Settings
from auth_entry_portal.security.cookies import decode_session_id, encode_session_id
from auth_entry_portal.security.passwords import hash_password, verify_password
from auth_entry_portal.security.rate_limit import FailedSignInLimiter
from auth_entry_portal.services.audit_service import sanitized_context
from auth_entry_portal.services.service_admin_service import ServiceValidationError, validate_destination
from auth_entry_portal.web.routes.auth import safe_return_to


def test_password_hash_and_verify():
    digest = hash_password("a-strong-password")
    assert "a-strong-password" not in digest
    assert verify_password(digest, "a-strong-password")
    assert not verify_password(digest, "wrong-password")


def test_signed_cookie_rejects_tampering():
    settings = Settings(secret_key="test-secret")
    value = encode_session_id("opaque-id", settings)
    assert decode_session_id(value, settings) == "opaque-id"
    assert decode_session_id(value + "tampered", settings) is None


def test_return_path_is_portal_local():
    assert safe_return_to("/services/demo") == "/services/demo"
    assert safe_return_to("//evil.test") == "/"
    assert safe_return_to("/admin/services") == "/"


def test_rate_limit_recovers_after_window():
    limiter = FailedSignInLimiter(2, 60)
    now = datetime.now(timezone.utc)
    limiter.failure("a", now=now)
    limiter.failure("a", now=now)
    assert limiter.blocked("a", now=now)
    assert not limiter.blocked("a", now=now + timedelta(seconds=61))


def test_destination_and_audit_safety():
    assert validate_destination("https://app.internal") == "https://app.internal"
    with pytest.raises(ServiceValidationError):
        validate_destination("https://user:secret@app.internal")
    assert sanitized_context({"correlation_id": "abc", "password": "secret"}) == {"correlation_id": "abc"}

