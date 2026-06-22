from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from auth_portal.config import Settings
from auth_portal.models import PortalSession, ProxyLaunchTicket, ServiceEntry, User
from auth_portal.security.cookies import decode_proxy_credential
from auth_portal.services.access_service import may_enter
from auth_portal.services.audit_service import sanitized_context
from auth_portal.services.session_service import as_utc, validate_session


class ProxyAuthorizationError(PermissionError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass(slots=True)
class ProxyIdentity:
    session: PortalSession
    user: User
    service: ServiceEntry


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ticket_digest(token: str, settings: Settings) -> str:
    return hmac.new(settings.secret_key.encode(), token.encode(), hashlib.sha256).hexdigest()


def issue_launch_ticket(
    db: Session,
    portal_session: PortalSession,
    service: ServiceEntry,
    settings: Settings,
    context: dict | None = None,
) -> str:
    token = secrets.token_urlsafe(32)
    now = utcnow()
    db.add(
        ProxyLaunchTicket(
            token_digest=ticket_digest(token, settings),
            session_id=portal_session.id,
            service_entry_id=service.id,
            created_at=now,
            expires_at=now + timedelta(seconds=settings.proxy_launch_ttl_seconds),
            request_context=sanitized_context(context),
        )
    )
    db.commit()
    return token


def consume_launch_ticket(db: Session, token: str, service: ServiceEntry, settings: Settings) -> ProxyIdentity:
    digest = ticket_digest(token, settings)
    ticket = db.scalar(select(ProxyLaunchTicket).where(ProxyLaunchTicket.token_digest == digest))
    now = utcnow()
    if (
        ticket is None
        or ticket.service_entry_id != service.id
        or ticket.consumed_at is not None
        or as_utc(ticket.expires_at) <= now
    ):
        raise ProxyAuthorizationError("invalid_launch_ticket")
    result = validate_session(db, ticket.session_id)
    if not result:
        raise ProxyAuthorizationError("invalid_session")
    portal_session, user = result
    db.refresh(service)
    if service.status != "enabled" or not service.proxy_enabled or not may_enter(db, user, service):
        raise ProxyAuthorizationError("not_authorized")
    changed = db.execute(
        update(ProxyLaunchTicket)
        .where(ProxyLaunchTicket.id == ticket.id, ProxyLaunchTicket.consumed_at.is_(None))
        .values(consumed_at=now)
    )
    if changed.rowcount != 1:
        db.rollback()
        raise ProxyAuthorizationError("invalid_launch_ticket")
    db.commit()
    return ProxyIdentity(portal_session, user, service)


def authorize_proxy_cookie(db: Session, cookie_value: str | None, service: ServiceEntry, settings: Settings) -> ProxyIdentity:
    credential = decode_proxy_credential(cookie_value, settings)
    if not credential:
        raise ProxyAuthorizationError("invalid_proxy_credential")
    session_id, service_id = credential
    if service_id != service.id:
        raise ProxyAuthorizationError("service_mismatch")
    result = validate_session(db, session_id)
    if not result:
        raise ProxyAuthorizationError("invalid_session")
    portal_session, user = result
    db.refresh(service)
    if service.status != "enabled" or not service.proxy_enabled:
        raise ProxyAuthorizationError("service_unavailable")
    if not may_enter(db, user, service):
        raise ProxyAuthorizationError("not_authorized")
    return ProxyIdentity(portal_session, user, service)
