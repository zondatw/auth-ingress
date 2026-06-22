from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from auth_entry_portal.config import Settings, get_settings
from auth_entry_portal.models import PortalSession, User
from auth_entry_portal.repositories.database import get_db
from auth_entry_portal.security.cookies import decode_session_id
from auth_entry_portal.services.session_service import validate_session


@dataclass(slots=True)
class Identity:
    session: PortalSession
    user: User


def optional_identity(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Identity | None:
    signed_id = request.cookies.get(settings.session_cookie)
    result = validate_session(db, decode_session_id(signed_id, settings))
    return Identity(*result) if result else None


def require_identity(identity: Identity | None = Depends(optional_identity)) -> Identity:
    if identity is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return identity


def require_admin(identity: Identity = Depends(require_identity)) -> Identity:
    if not identity.user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return identity

