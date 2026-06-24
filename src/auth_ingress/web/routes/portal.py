from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth_ingress.config import Settings, get_settings
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
    return template(request, "portal/index.html", settings, user=identity.user, services=list_permitted_services(db, identity.user))
