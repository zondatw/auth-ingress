from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth_portal.repositories.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ServiceEntry(Base):
    __tablename__ = "service_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(500))
    destination: Mapped[str] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(16), default="enabled")
    proxy_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    websocket_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    external_redirect_policy: Mapped[str] = mapped_column(String(16), default="deny", server_default="deny")
    compatibility_status: Mapped[str] = mapped_column(String(16), default="unchecked", server_default="unchecked")
    compatibility_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    compatibility_summary: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    rules: Mapped[list[AccessRule]] = relationship(back_populates="service_entry", cascade="all, delete-orphan")


class AccessRule(Base):
    __tablename__ = "access_rules"
    __table_args__ = (UniqueConstraint("service_entry_id", "group_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    service_entry_id: Mapped[int] = mapped_column(ForeignKey("service_entries.id", ondelete="CASCADE"))
    rule_type: Mapped[str] = mapped_column(String(20), default="group")
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    service_entry: Mapped[ServiceEntry] = relationship(back_populates="rules")
