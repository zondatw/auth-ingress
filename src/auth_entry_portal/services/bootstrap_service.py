from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from auth_entry_portal.models import InstallationState, User
from auth_entry_portal.security.passwords import hash_password
from auth_entry_portal.services.audit_service import record_event


class BootstrapError(RuntimeError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


def is_bootstrap_required(db: Session) -> bool:
    state = db.get(InstallationState, 1)
    count = db.scalar(select(func.count()).select_from(User)) or 0
    return count == 0 and (state is None or state.state == "needs_bootstrap")


def mark_installation_initialized(db: Session) -> None:
    now = datetime.now(timezone.utc)
    state = db.get(InstallationState, 1)
    if state is None:
        state = InstallationState(id=1)
        db.add(state)
    state.state = "initialized"
    state.revision = (state.revision or 0) + 1
    state.initialized_at = state.initialized_at or now
    state.updated_at = now


def bootstrap_admin(db: Session, email: str, display_name: str, password: str) -> User:
    canonical_name = display_name.strip()
    if not canonical_name:
        raise BootstrapError("invalid_input", "Display name is required")
    try:
        password_hash = hash_password(password)
        if db.bind is not None and db.bind.dialect.name == "sqlite":
            db.execute(text("BEGIN IMMEDIATE"))
        state = db.get(InstallationState, 1)
        if state is None:
            state = InstallationState(id=1, state="needs_bootstrap")
            db.add(state)
            db.flush()
        elif db.bind is not None and db.bind.dialect.name != "sqlite":
            state = db.scalar(select(InstallationState).where(InstallationState.id == 1).with_for_update())
        count = db.scalar(select(func.count()).select_from(User)) or 0
        if state.state != "needs_bootstrap" or count:
            db.rollback()
            raise BootstrapError("already_initialized", "Installation is already initialized")
        user = User(email=email, display_name=canonical_name, password_hash=password_hash, status="active", credential_status="active", is_admin=True)
        db.add(user)
        db.flush()
        mark_installation_initialized(db)
        record_event(
            db,
            "bootstrap_succeeded",
            "changed",
            "first_admin_created",
            target_user_id=user.id,
            context={"client_category": "local_cli"},
            change_summary={"revision": user.revision, "field_names": ["email", "display_name", "is_admin"]},
            commit=False,
        )
        db.commit()
        db.refresh(user)
        return user
    except BootstrapError:
        raise
    except (IntegrityError, OperationalError) as error:
        db.rollback()
        raise BootstrapError("conflict", "Bootstrap could not acquire the installation state") from error
    except Exception:
        db.rollback()
        raise
