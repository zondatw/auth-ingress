from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_ingress.config import Settings, get_settings
from auth_ingress.models import AccessRule, Group, ServiceEntry
from auth_ingress.repositories.database import get_db
from auth_ingress.security.csrf import valid_csrf
from auth_ingress.security.dependencies import Identity, require_admin
from auth_ingress.services.audit_service import record_event
from auth_ingress.services.service_admin_service import ServiceValidationError, save_service
from auth_ingress.services.service_compatibility_service import check_service_compatibility
from auth_ingress.security.proxy_host import service_origin
from auth_ingress.web.web import template

router = APIRouter(prefix="/admin")


def page(request: Request, db: Session, settings: Settings, identity: Identity, *, error: str | None = None, status_code: int = 200):
    services = list(db.scalars(select(ServiceEntry).order_by(ServiceEntry.display_name)).all())
    groups = list(db.scalars(select(Group).order_by(Group.name)).all())
    service_group_names: dict[int, list[str]] = {}
    assigned_groups = db.execute(
        select(AccessRule.service_entry_id, Group.name)
        .join(Group, Group.id == AccessRule.group_id)
        .order_by(Group.name)
    )
    for service_entry_id, group_name in assigned_groups:
        service_group_names.setdefault(service_entry_id, []).append(group_name)
    return template(
        request,
        "admin/services.html",
        settings,
        user=identity.user,
        services=services,
        groups=groups,
        service_group_names={service_id: ", ".join(names) for service_id, names in service_group_names.items()},
        service_origins={service.id: service_origin(service.slug, settings) for service in services},
        error=error,
        status_code=status_code,
    )


@router.get("/services")
def list_services(
    request: Request,
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return page(request, db, settings, identity)


def persist(
    request: Request,
    identity: Identity,
    db: Session,
    settings: Settings,
    original_slug: str | None,
    slug: str,
    display_name: str,
    description: str,
    destination: str,
    status: str,
    group_names: str,
    csrf: str,
    proxy_enabled: bool = False,
    websocket_enabled: bool = False,
):
    if not valid_csrf(csrf, settings):
        return page(request, db, settings, identity, error="The form expired. Please try again.", status_code=400)
    try:
        service, action = save_service(
            db,
            original_slug=original_slug,
            slug=slug,
            display_name=display_name,
            description=description,
            destination=destination,
            status=status,
            group_names=group_names.split(","),
            proxy_enabled=proxy_enabled,
            websocket_enabled=websocket_enabled,
        )
    except ServiceValidationError as exc:
        db.rollback()
        return page(request, db, settings, identity, error=str(exc), status_code=400)
    record_event(
        db,
        f"service_entry_{action}",
        "changed",
        action,
        actor_user_id=identity.user.id,
        service_entry_id=service.id,
        context={"correlation_id": getattr(request.state, "correlation_id", ""), "client_category": "browser"},
    )
    return page(request, db, settings, identity, status_code=201 if action == "created" else 200)


@router.post("/services")
def create_service(
    request: Request,
    slug: str = Form(...),
    display_name: str = Form(...),
    description: str = Form(""),
    destination: str = Form(...),
    status: str = Form(...),
    group_names: str = Form(""),
    csrf: str = Form(...),
    proxy_enabled: bool = Form(False),
    websocket_enabled: bool = Form(False),
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return persist(request, identity, db, settings, None, slug, display_name, description, destination, status, group_names, csrf, proxy_enabled, websocket_enabled)


@router.post("/services/{service_slug}")
def update_service(
    service_slug: str,
    request: Request,
    slug: str = Form(...),
    display_name: str = Form(...),
    description: str = Form(""),
    destination: str = Form(...),
    status: str = Form(...),
    group_names: str = Form(""),
    csrf: str = Form(...),
    proxy_enabled: bool = Form(False),
    websocket_enabled: bool = Form(False),
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not db.scalar(select(ServiceEntry).where(ServiceEntry.slug == service_slug)):
        return template(request, "errors/access_denied.html", settings, title="Service not found", message="The service entry does not exist.", status_code=404)
    return persist(request, identity, db, settings, service_slug, slug, display_name, description, destination, status, group_names, csrf, proxy_enabled, websocket_enabled)


@router.post("/services/{service_slug}/compatibility")
async def check_compatibility(
    service_slug: str,
    request: Request,
    csrf: str = Form(...),
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == service_slug))
    if not service:
        return template(request, "errors/access_denied.html", settings, title="Service not found", message="The service entry does not exist.", status_code=404)
    if not valid_csrf(csrf, settings):
        return page(request, db, settings, identity, error="The form expired. Please try again.", status_code=400)
    status, summary = await check_service_compatibility(db, service, settings)
    record_event(
        db,
        "proxy_compatibility_checked",
        "informational",
        status,
        actor_user_id=identity.user.id,
        service_entry_id=service.id,
        context={"correlation_id": getattr(request.state, "correlation_id", ""), "client_category": "browser"},
    )
    return page(request, db, settings, identity, error=f"Compatibility: {status} ({summary})")
