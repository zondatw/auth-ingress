from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_entry_portal.config import Settings, get_settings
from auth_entry_portal.models import ServiceEntry
from auth_entry_portal.repositories.database import get_db
from auth_entry_portal.security.dependencies import Identity, optional_identity
from auth_entry_portal.services.access_service import may_enter
from auth_entry_portal.services.audit_service import record_event
from auth_entry_portal.services.downstream_service import DownstreamUnavailable, fetch_downstream
from auth_entry_portal.services.proxy_authorization_service import issue_launch_ticket
from auth_entry_portal.security.proxy_host import service_origin
from auth_entry_portal.web.web import template

router = APIRouter()


def ctx(request: Request) -> dict:
    return {"correlation_id": getattr(request.state, "correlation_id", ""), "client_category": "browser"}


@router.get("/services/{service_slug}")
async def enter_service(
    service_slug: str,
    request: Request,
    identity: Identity | None = Depends(optional_identity),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not identity:
        return RedirectResponse(f"/sign-in?return_to=/services/{service_slug}", status_code=302)
    service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == service_slug))
    if service is None:
        record_event(db, "service_entry_denied", "denied", "unknown_service", actor_user_id=identity.user.id, context=ctx(request))
        return template(request, "errors/access_denied.html", settings, title="Service not found", message="This service is unavailable. Return to your service list.", status_code=404)
    if service.status != "enabled":
        record_event(db, "service_entry_denied", "denied", "service_disabled", actor_user_id=identity.user.id, service_entry_id=service.id, context=ctx(request))
        return template(request, "errors/access_denied.html", settings, title="Service unavailable", message="This service is currently unavailable. Return to your service list.", status_code=503)
    if not may_enter(db, identity.user, service):
        record_event(db, "service_entry_denied", "denied", "not_authorized", actor_user_id=identity.user.id, service_entry_id=service.id, context=ctx(request))
        return template(request, "errors/access_denied.html", settings, title="Access denied", message="You are not authorized for this service. Return to your service list.", status_code=403)
    if service.proxy_enabled:
        ticket = issue_launch_ticket(
            db,
            identity.session,
            service,
            settings,
            context={"correlation_id": getattr(request.state, "correlation_id", ""), "client_category": "browser"},
        )
        record_event(db, "proxy_launch_created", "allowed", "ticket_issued", actor_user_id=identity.user.id, service_entry_id=service.id, context=ctx(request))
        return RedirectResponse(
            f"{service_origin(service.slug, settings)}/__portal/bootstrap?ticket={ticket}",
            status_code=302,
            headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
        )
    try:
        body, content_type = await fetch_downstream(service.destination, settings.downstream_timeout_seconds)
    except DownstreamUnavailable:
        record_event(db, "service_entry_denied", "denied", "downstream_unavailable", actor_user_id=identity.user.id, service_entry_id=service.id, context=ctx(request))
        return template(request, "errors/access_denied.html", settings, title="Service unavailable", message="The service could not be reached. Try again later.", status_code=503)
    record_event(db, "service_entry_allowed", "allowed", "access_rule_matched", actor_user_id=identity.user.id, service_entry_id=service.id, context=ctx(request))
    return Response(body, media_type=content_type, headers={"Cache-Control": "no-store"})
