from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth_ingress.config import Settings, get_settings
from auth_ingress.models import AuditEvent
from auth_ingress.repositories.database import get_db
from auth_ingress.security.dependencies import Identity, require_admin
from auth_ingress.web.web import template

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
    retained_count = db.scalar(select(func.count(AuditEvent.id)).where(AuditEvent.created_at >= retained_since)) or 0
    recent_since = datetime.now(timezone.utc) - timedelta(days=1)
    recent_denials = db.scalar(
        select(func.count(AuditEvent.id)).where(
            AuditEvent.created_at >= recent_since,
            AuditEvent.decision.in_(("denied", "rejected")),
        )
    ) or 0
    summary = [
        {"label": "Retained events", "value": retained_count, "status": "neutral", "hint": f"Events within {settings.audit_retention_days} day retention."},
        {"label": "Recent denials", "value": recent_denials, "status": "warning" if recent_denials else "success", "hint": "Denied or rejected events in the last 24 hours."},
        {"label": "Current page", "value": len(events), "status": "neutral", "hint": "Events loaded in this view."},
    ]
    return template(request, "admin/audit.html", settings, user=identity.user, events=events, page=page, summary=summary)
