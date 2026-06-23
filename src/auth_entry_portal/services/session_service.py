from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_entry_portal.models import PortalSession, User


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def create_session(db: Session, user: User, ttl_seconds: int) -> PortalSession:
    now = utcnow()
    portal_session = PortalSession(
        id=secrets.token_urlsafe(32),
        user_id=user.id,
        created_at=now,
        expires_at=now + timedelta(seconds=ttl_seconds),
        last_seen_at=now,
    )
    db.add(portal_session)
    db.commit()
    return portal_session


def validate_session(db: Session, session_id: str | None) -> tuple[PortalSession, User] | None:
    if not session_id:
        return None
    portal_session = db.get(PortalSession, session_id)
    now = utcnow()
    if not portal_session or portal_session.revoked_at is not None or as_utc(portal_session.expires_at) <= now:
        return None
    user = db.get(User, portal_session.user_id)
    if not user or user.status != "active":
        return None
    portal_session.last_seen_at = now
    db.commit()
    return portal_session, user


def revoke_session(db: Session, portal_session: PortalSession | None) -> None:
    if portal_session and portal_session.revoked_at is None:
        portal_session.revoked_at = utcnow()
        db.commit()


def revoke_user_sessions(db: Session, user_id: int, *, commit: bool = False) -> int:
    now = utcnow()
    sessions = list(db.scalars(select(PortalSession).where(PortalSession.user_id == user_id, PortalSession.revoked_at.is_(None))).all())
    for portal_session in sessions:
        portal_session.revoked_at = now
    if commit:
        db.commit()
    return len(sessions)
