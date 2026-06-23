from __future__ import annotations

from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth_entry_portal.config import Settings, get_settings
from auth_entry_portal.repositories.database import get_db
from auth_entry_portal.security.cookies import cookie_options, decode_session_id, encode_session_id
from auth_entry_portal.security.csrf import valid_csrf
from auth_entry_portal.security.rate_limit import FailedSignInLimiter
from auth_entry_portal.services.audit_service import record_event
from auth_entry_portal.services.authentication_service import authenticate, normalize_email
from auth_entry_portal.services.bootstrap_service import is_bootstrap_required
from auth_entry_portal.services.session_service import create_session, revoke_session, validate_session
from auth_entry_portal.web.web import template

router = APIRouter()
_limiters: dict[tuple[int, int], FailedSignInLimiter] = {}


def safe_return_to(value: str | None) -> str:
    if not value:
        return "/"
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/") or parsed.path.startswith("//"):
        return "/"
    if not (parsed.path == "/" or parsed.path.startswith("/services/")):
        return "/"
    return parsed.path


def limiter(settings: Settings) -> FailedSignInLimiter:
    key = (settings.rate_limit_attempts, settings.rate_limit_window_seconds)
    return _limiters.setdefault(key, FailedSignInLimiter(*key))


def context(request: Request) -> dict:
    return {"correlation_id": getattr(request.state, "correlation_id", ""), "client_category": "browser"}


@router.get("/sign-in")
def sign_in_form(request: Request, return_to: str | None = None, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if is_bootstrap_required(db):
        return template(request, "auth/setup_required.html", settings, status_code=503)
    return template(request, "auth/sign_in.html", settings, return_to=safe_return_to(return_to), error=None)


@router.post("/sign-in")
def sign_in(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    return_to: str = Form("/"),
    csrf: str = Form(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if is_bootstrap_required(db):
        return template(request, "auth/setup_required.html", settings, status_code=503)
    if not valid_csrf(csrf, settings):
        return template(request, "auth/sign_in.html", settings, return_to="/", error="The form expired. Please try again.", status_code=400)
    email_key = f"account:{normalize_email(email)}"
    client_key = f"client:{request.client.host if request.client else 'unknown'}"
    gate = limiter(settings)
    if gate.blocked(email_key, client_key):
        record_event(db, "sign_in_failure", "denied", "rate_limited", context=context(request))
        return template(request, "auth/sign_in.html", settings, return_to=safe_return_to(return_to), error="Too many attempts. Wait a few minutes and try again.", status_code=429)
    user = authenticate(db, email, password)
    if not user:
        gate.failure(email_key, client_key)
        record_event(db, "sign_in_failure", "denied", "invalid_credentials", context=context(request))
        return template(request, "auth/sign_in.html", settings, return_to=safe_return_to(return_to), error="Email or password was not accepted.", status_code=401)
    gate.success(email_key, client_key)
    portal_session = create_session(db, user, settings.session_ttl_seconds)
    record_event(db, "sign_in_success", "allowed", "credentials_valid", actor_user_id=user.id, context=context(request))
    response = RedirectResponse(safe_return_to(return_to), status_code=302)
    response.set_cookie(settings.session_cookie, encode_session_id(portal_session.id, settings), **cookie_options(settings))
    return response


@router.post("/sign-out")
def sign_out(
    request: Request,
    csrf: str = Form(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not valid_csrf(csrf, settings):
        return template(request, "errors/access_denied.html", settings, title="Request expired", message="Please return to the portal and try again.", status_code=400)
    session_id = decode_session_id(request.cookies.get(settings.session_cookie), settings)
    result = validate_session(db, session_id)
    if result:
        portal_session, user = result
        revoke_session(db, portal_session)
        record_event(db, "sign_out", "informational", "user_requested", actor_user_id=user.id, context=context(request))
    response = RedirectResponse("/sign-in?signed_out=1", status_code=302)
    response.delete_cookie(settings.session_cookie, path="/")
    return response
