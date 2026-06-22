from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth_portal.models import User
from auth_portal.security.passwords import verify_password


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(func.lower(User.email) == normalize_email(email)))
    if not verify_password(user.password_hash if user else None, password):
        return None
    return user if user.status == "active" else None

