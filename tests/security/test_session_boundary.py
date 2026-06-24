from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from auth_ingress.models import PortalSession, User
from tests.conftest import sign_in


def test_cookie_is_httponly_and_samesite(client, csrf):
    response = sign_in(client, csrf)
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_rejects_external_return_path(client, csrf):
    response = sign_in(client, csrf, return_to="https://evil.test/steal")
    assert response.headers["location"] == "/"


def test_sign_out_revokes_browser_history_access(client, csrf):
    sign_in(client, csrf)
    assert client.get("/services/demo").status_code == 200
    client.post("/sign-out", data={"csrf": csrf})
    assert client.get("/services/demo", follow_redirects=False).status_code == 302


def test_expired_session_is_rejected(client, csrf, db_factory):
    sign_in(client, csrf)
    with db_factory() as db:
        session = db.scalar(select(PortalSession))
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert client.get("/", follow_redirects=False).status_code == 302


def test_disabled_user_cannot_sign_in(client, csrf):
    response = sign_in(client, csrf, email="disabled@example.test")
    assert response.status_code == 401
    assert "Email or password was not accepted" in response.text

