from __future__ import annotations

from datetime import datetime, timezone

from auth_ingress import models  # noqa: F401
from sqlalchemy import inspect, text

from auth_ingress.repositories.database import Base, engine


SERVICE_ENTRY_UPGRADES = {
    "proxy_enabled": "BOOLEAN NOT NULL DEFAULT 0",
    "websocket_enabled": "BOOLEAN NOT NULL DEFAULT 0",
    "external_redirect_policy": "VARCHAR(16) NOT NULL DEFAULT 'deny'",
    "compatibility_status": "VARCHAR(16) NOT NULL DEFAULT 'unchecked'",
    "compatibility_checked_at": "DATETIME",
    "compatibility_summary": "VARCHAR(500)",
}
USER_UPGRADES = {
    "normalized_email": "VARCHAR(320)",
    "credential_status": "VARCHAR(24) NOT NULL DEFAULT 'active'",
    "revision": "INTEGER NOT NULL DEFAULT 1",
}
AUDIT_UPGRADES = {
    "target_user_id": "INTEGER",
    "change_summary": "JSON NOT NULL DEFAULT '{}'",
}


def _add_columns(bind, table: str, upgrades: dict[str, str]) -> None:
    inspector = inspect(bind)
    if table not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns(table)}
    missing = {name: definition for name, definition in upgrades.items() if name not in existing}
    if not missing:
        return
    if bind.dialect.name != "sqlite":
        raise RuntimeError(f"schema migration required for {table}")
    with bind.begin() as connection:
        for name, definition in missing.items():
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))


def _backfill_normalized_emails(bind) -> None:
    inspector = inspect(bind)
    if "users" not in inspector.get_table_names() or "normalized_email" not in {c["name"] for c in inspector.get_columns("users")}:
        return
    with bind.begin() as connection:
        rows = connection.execute(text("SELECT id, email, normalized_email FROM users ORDER BY id")).all()
        seen: dict[str, int] = {}
        for user_id, email, normalized in rows:
            value = (normalized or email or "").strip().casefold()
            if not value or "@" not in value:
                raise RuntimeError("invalid normalized email during schema upgrade")
            if value in seen and seen[value] != user_id:
                raise RuntimeError("normalized email collision during schema upgrade")
            seen[value] = user_id
            connection.execute(
                text("UPDATE users SET email = trim(email), normalized_email = :value WHERE id = :user_id"),
                {"value": value, "user_id": user_id},
            )
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_normalized_email ON users (normalized_email)"))


def upgrade_existing_schema(bind=engine) -> None:
    _add_columns(bind, "service_entries", SERVICE_ENTRY_UPGRADES)
    _add_columns(bind, "users", USER_UPGRADES)
    _add_columns(bind, "audit_events", AUDIT_UPGRADES)
    _backfill_normalized_emails(bind)


def _ensure_installation_state(bind) -> None:
    with bind.begin() as connection:
        existing = connection.execute(text("SELECT state FROM installation_state WHERE id = 1")).scalar_one_or_none()
        user_count = connection.execute(text("SELECT count(*) FROM users")).scalar_one()
        desired = "initialized" if user_count else "needs_bootstrap"
        if existing is None:
            connection.execute(
                text("INSERT INTO installation_state (id, state, revision, initialized_at, updated_at) VALUES (1, :state, 1, :initialized_at, :updated_at)"),
                {
                    "state": desired,
                    "initialized_at": datetime.now(timezone.utc) if user_count else None,
                    "updated_at": datetime.now(timezone.utc),
                },
            )
        elif existing == "needs_bootstrap" and user_count:
            connection.execute(
                text("UPDATE installation_state SET state = 'initialized', revision = revision + 1, initialized_at = :now, updated_at = :now WHERE id = 1"),
                {"now": datetime.now(timezone.utc)},
            )


def create_schema(bind=engine) -> None:
    upgrade_existing_schema(bind)
    Base.metadata.create_all(bind)
    _ensure_installation_state(bind)


def drop_schema(bind=engine) -> None:
    Base.metadata.drop_all(bind)
