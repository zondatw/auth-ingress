from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_ingress.config import Settings, get_settings
from auth_ingress.models import ServiceEntry
from auth_ingress.repositories.database import get_db
from auth_ingress.security.dependencies import Identity, optional_identity
from auth_ingress.services.access_service import list_permitted_services
from auth_ingress.web.web import template

router = APIRouter()


@router.get("/")
def home(
    request: Request,
    identity: Identity | None = Depends(optional_identity),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not identity:
        return RedirectResponse("/sign-in", status_code=302)
    if identity.user.credential_status == "temporary":
        return RedirectResponse("/change-password", status_code=302)
    services = list_permitted_services(db, identity.user)
    total_services = len(list(db.scalars(select(ServiceEntry.id)).all()))
    summary = [
        {"label": "Assigned services", "value": len(services), "status": "success" if services else "warning", "hint": "Services currently reachable by this account."},
        {"label": "Directory entries", "value": total_services, "status": "neutral", "hint": "Configured service entries in the portal."},
        {"label": "Admin console", "value": "Enabled" if identity.user.is_admin else "Hidden", "status": "success" if identity.user.is_admin else "disabled", "hint": "Management navigation follows your authorization state."},
    ]
    return template(request, "portal/index.html", settings, user=identity.user, services=services, summary=summary)
