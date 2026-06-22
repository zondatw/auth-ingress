from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from auth_portal.repositories.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProxyLaunchTicket(Base):
    __tablename__ = "proxy_launch_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_digest: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    service_entry_id: Mapped[int] = mapped_column(ForeignKey("service_entries.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    request_context: Mapped[dict] = mapped_column(JSON, default=dict)
