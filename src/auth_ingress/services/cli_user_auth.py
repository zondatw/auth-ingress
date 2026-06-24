from __future__ import annotations

from auth_ingress.models import User
from auth_ingress.security.rate_limit import FailedSignInLimiter
from auth_ingress.services.authentication_service import authenticate, normalize_email
from sqlalchemy.orm import Session

_limiter = FailedSignInLimiter(5, 300)


def authenticate_cli_actor(db: Session, email: str, password: str) -> User | None:
    key = f"cli:{normalize_email(email)}"
    if _limiter.blocked(key):
        return None
    user = authenticate(db, email, password)
    if user is None or user.credential_status != "active" or not user.is_admin:
        _limiter.failure(key)
        return None
    _limiter.success(key)
    return user
