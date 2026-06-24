from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from auth_ingress.repositories.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InstallationState(Base):
    __tablename__ = "installation_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    state: Mapped[str] = mapped_column(String(24), default="needs_bootstrap")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    initialized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
