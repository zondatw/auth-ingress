from auth_entry_portal import models  # noqa: F401
from sqlalchemy import inspect, text

from auth_entry_portal.repositories.database import Base, engine


SERVICE_ENTRY_UPGRADES = {
    "proxy_enabled": "BOOLEAN NOT NULL DEFAULT 0",
    "websocket_enabled": "BOOLEAN NOT NULL DEFAULT 0",
    "external_redirect_policy": "VARCHAR(16) NOT NULL DEFAULT 'deny'",
    "compatibility_status": "VARCHAR(16) NOT NULL DEFAULT 'unchecked'",
    "compatibility_checked_at": "DATETIME",
    "compatibility_summary": "VARCHAR(500)",
}


def upgrade_existing_schema(bind=engine) -> None:
    inspector = inspect(bind)
    if "service_entries" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("service_entries")}
    missing = {name: definition for name, definition in SERVICE_ENTRY_UPGRADES.items() if name not in existing}
    if not missing:
        return
    if bind.dialect.name != "sqlite":
        raise RuntimeError("schema migration required before starting the proxy feature")
    with bind.begin() as connection:
        for name, definition in missing.items():
            connection.execute(text(f"ALTER TABLE service_entries ADD COLUMN {name} {definition}"))


def create_schema(bind=engine) -> None:
    upgrade_existing_schema(bind)
    Base.metadata.create_all(bind)


def drop_schema(bind=engine) -> None:
    Base.metadata.drop_all(bind)
