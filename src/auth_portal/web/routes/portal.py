from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth_portal.config import Settings, get_settings
from auth_portal.repositories.database import get_db
from auth_portal.security.dependencies import Identity, optional_identity
from auth_portal.services.access_service import list_permitted_services
from auth_portal.web.web import template

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
    return template(request, "portal/index.html", settings, user=identity.user, services=list_permitted_services(db, identity.user))

