from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_entry_portal.config import Settings, get_settings
from auth_entry_portal.models import AuditEvent
from auth_entry_portal.repositories.database import get_db
from auth_entry_portal.security.dependencies import Identity, require_admin
from auth_entry_portal.web.web import template

router = APIRouter(prefix="/admin")


@router.get("/audit")
def audit_events(
    request: Request,
    page: int = 1,
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    page = max(page, 1)
    retained_since = datetime.now(timezone.utc) - timedelta(days=settings.audit_retention_days)
    events = list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.created_at >= retained_since)
            .order_by(AuditEvent.created_at.desc())
            .offset((page - 1) * 100)
            .limit(100)
        ).all()
    )
    return template(request, "admin/audit.html", settings, user=identity.user, events=events, page=page)

