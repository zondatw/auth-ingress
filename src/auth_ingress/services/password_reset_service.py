from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from urllib.parse import quote

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from auth_ingress.config import Settings
from auth_ingress.models import PasswordResetRequest, User
from auth_ingress.security.passwords import hash_password
from auth_ingress.services.audit_service import record_event
from auth_ingress.services.recovery_delivery import RecoveryDelivery
from auth_ingress.services.session_service import as_utc, revoke_user_sessions
from auth_ingress.services.user_management_types import ManagementError, OutcomeCode


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt="auth-portal-password-reset-v1")


def encode_reset_cookie(token: str, settings: Settings) -> str:
    return _serializer(settings).dumps({"reset": token})


def decode_reset_cookie(cookie: str | None, settings: Settings) -> str:
    try:
        payload = _serializer(settings).loads(cookie or "", max_age=settings.password_reset_ttl_seconds)
        token = payload.get("reset")
        if not isinstance(token, str) or not token:
            raise BadSignature("missing token")
        return token
    except (BadSignature, SignatureExpired) as error:
        raise ManagementError(OutcomeCode.INVALID_INPUT, "Reset request is invalid or expired") from error


def _active_request(db: Session, token: str) -> PasswordResetRequest:
    request = db.scalar(select(PasswordResetRequest).where(PasswordResetRequest.token_digest == token_digest(token)))
    if request is None or request.consumed_at is not None or request.invalidated_at is not None or as_utc(request.expires_at) <= utcnow():
        raise ManagementError(OutcomeCode.INVALID_INPUT, "Reset request is invalid or expired")
    return request


def validate_reset_token(db: Session, token: str) -> None:
    _active_request(db, token)


def initiate_reset(db: Session, actor: User, target: User, settings: Settings, delivery: RecoveryDelivery, base_url: str) -> PasswordResetRequest:
    now = utcnow()
    active_requests = list(db.scalars(select(PasswordResetRequest).where(PasswordResetRequest.user_id == target.id, PasswordResetRequest.consumed_at.is_(None), PasswordResetRequest.invalidated_at.is_(None))).all())
    for active in active_requests:
        active.invalidated_at = now
    raw = secrets.token_urlsafe(32)
    request = PasswordResetRequest(user_id=target.id, token_digest=token_digest(raw), expires_at=now + timedelta(seconds=settings.password_reset_ttl_seconds), requested_by_user_id=actor.id)
    db.add(request)
    record_event(db, "password_reset_requested", "changed", "delivery_pending", actor_user_id=actor.id, target_user_id=target.id, context={"client_category": "management"}, commit=False)
    db.commit()
    try:
        delivery.send(target.email, f"{base_url.rstrip('/')}/reset-password?token={quote(raw)}")
    except Exception as error:
        request.invalidated_at = utcnow()
        record_event(db, "password_reset_delivery_failed", "denied", "delivery_failed", actor_user_id=actor.id, target_user_id=target.id, context={"client_category": "management"}, commit=False)
        db.commit()
        raise ManagementError(OutcomeCode.DEPENDENCY_FAILURE, "Recovery delivery failed") from error
    return request


def complete_reset(db: Session, cookie: str | None, password: str, settings: Settings) -> User:
    raw = decode_reset_cookie(cookie, settings)
    request = _active_request(db, raw)
    user = db.get(User, request.user_id)
    if user is None:
        raise ManagementError(OutcomeCode.INVALID_INPUT, "Reset request is invalid or expired")
    try:
        user.password_hash = hash_password(password)
        user.credential_status = "active"
        user.revision += 1
        request.consumed_at = utcnow()
        revoke_user_sessions(db, user.id)
        record_event(db, "password_reset_completed", "changed", "credential_replaced", target_user_id=user.id, context={"client_category": "browser"}, change_summary={"revision": user.revision, "field_names": ["credential_status"]}, commit=False)
        db.commit()
        return user
    except Exception:
        db.rollback()
        raise
