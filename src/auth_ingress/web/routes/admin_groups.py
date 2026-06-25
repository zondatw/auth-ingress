from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth_ingress.config import Settings, get_settings
from auth_ingress.models import AccessRule, Group
from auth_ingress.repositories.database import get_db
from auth_ingress.security.csrf import valid_csrf
from auth_ingress.security.dependencies import Identity, require_admin
from auth_ingress.security.rate_limit import ManagementRequestLimiter
from auth_ingress.services.audit_service import record_event
from auth_ingress.services.group_admin_service import (
    GroupOperationResult,
    GroupValidationError,
    create_group,
    deactivate_group,
    group_detail,
    reactivate_group,
    remove_group,
    search_groups,
    update_group,
)
from auth_ingress.services.user_management_types import FieldError, ManagementFormState, OutcomeCode
from auth_ingress.web.web import template

router = APIRouter(prefix="/admin/groups")
_limiters: dict[tuple[int, int], ManagementRequestLimiter] = {}


def limiter(settings: Settings) -> ManagementRequestLimiter:
    key = (settings.management_rate_limit_attempts, settings.management_rate_limit_window_seconds)
    return _limiters.setdefault(key, ManagementRequestLimiter(*key))


def _group_summary(db: Session, groups: list | None = None) -> list[dict[str, object]]:
    active = db.scalar(select(func.count(Group.id)).where(Group.status == "active")) or 0
    deactivated = db.scalar(select(func.count(Group.id)).where(Group.status == "deactivated")) or 0
    used = db.scalar(select(func.count(func.distinct(AccessRule.group_id)))) or 0
    total = active + deactivated
    return [
        {"label": "Active groups", "value": active, "status": "success", "hint": "Groups currently able to grant service access."},
        {"label": "Deactivated", "value": deactivated, "status": "disabled" if deactivated else "neutral", "hint": "Groups preserved but not granting access."},
        {"label": "Linked to services", "value": used, "status": "neutral", "hint": "Groups referenced by one or more service rules."},
        {"label": "Unused groups", "value": max(total - used, 0), "status": "warning" if total - used else "neutral", "hint": "Groups with no current service dependency."},
    ]


def _group_detail_summary(group, dependencies) -> list[dict[str, object]]:
    return [
        {"label": "Lifecycle", "value": group.status, "status": "success" if group.status == "active" else "disabled", "hint": "Current group state."},
        {"label": "Assigned users", "value": dependencies.user_count, "status": "neutral", "hint": "Users directly assigned to this group."},
        {"label": "Associated services", "value": dependencies.service_count, "status": "neutral", "hint": "Services depending on this group."},
        {"label": "Revision", "value": group.revision, "status": "neutral", "hint": "Used to detect stale lifecycle changes."},
    ]


def group_form_state(
    form_name: str,
    *,
    name: str = "",
    description: str = "",
    expected_revision: int | None = None,
    record_id: int | None = None,
    error: str,
    field: str | None = None,
) -> ManagementFormState:
    values = {"name": name, "description": description}
    if expected_revision is not None:
        values["expected_revision"] = expected_revision
    return ManagementFormState.from_submitted(
        form_name,
        values,
        record_id=record_id,
        field_errors=[FieldError(field, error)] if field else [],
        form_errors=[] if field else [error],
    )


def list_page(
    request: Request,
    db: Session,
    settings: Settings,
    identity: Identity,
    *,
    q: str = "",
    status: str = "",
    usage: str = "",
    error: str | None = None,
    message: str | None = None,
    form_state: ManagementFormState | None = None,
    status_code: int = 200,
):
    groups = search_groups(db, query=q, status=status or None, usage=usage or None)
    return template(
        request,
        "admin/groups.html",
        settings,
        user=identity.user,
        groups=groups,
        filters={"q": q, "status": status, "usage": usage},
        error=error,
        message=message,
        form_state=form_state,
        summary=_group_summary(db, groups),
        status_code=status_code,
    )


def detail_page(
    request: Request,
    db: Session,
    settings: Settings,
    identity: Identity,
    group_id: int,
    *,
    error: str | None = None,
    message: str | None = None,
    preview: GroupOperationResult | None = None,
    form_state: ManagementFormState | None = None,
    status_code: int = 200,
):
    try:
        detail = group_detail(db, identity.user, group_id, audit=preview is None and error is None)
    except GroupValidationError as exc:
        return template(request, "errors/access_denied.html", settings, title="Group not found", message=str(exc), status_code=404)
    return template(
        request,
        "admin/group_detail.html",
        settings,
        user=identity.user,
        managed=detail["group"],
        dependencies=detail["dependencies"],
        audit_events=detail["events"],
        summary=_group_detail_summary(detail["group"], detail["dependencies"]),
        error=error,
        message=message,
        preview=preview,
        form_state=form_state,
        status_code=status_code,
    )


@router.get("")
def list_groups(
    request: Request,
    q: str = "",
    status: str = "",
    usage: str = "",
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if status not in {"", "active", "deactivated"} or usage not in {"", "used", "unused"}:
        return list_page(request, db, settings, identity, q=q, status="", usage="", error="Invalid group filters", status_code=400)
    if not limiter(settings).allow(f"group:list:{identity.user.id}"):
        return template(request, "errors/access_denied.html", settings, title="Too many requests", message="Wait and try again.", status_code=429)
    return list_page(request, db, settings, identity, q=q, status=status, usage=usage)


@router.post("")
def create_group_route(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    csrf: str = Form(...),
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not valid_csrf(csrf, settings):
        error = "The form expired. Please try again."
        return list_page(request, db, settings, identity, error=error, form_state=group_form_state("group_create", name=name, description=description, error=error), status_code=400)
    if not limiter(settings).allow(f"group:mutation:{identity.user.id}"):
        return list_page(request, db, settings, identity, error="Too many requests. Wait and try again.", status_code=429)
    try:
        result = create_group(db, identity.user, name, description)
    except GroupValidationError as exc:
        record_event(db, "group_create_rejected", "denied" if exc.code == OutcomeCode.DENIED else "rejected", exc.code.value, actor_user_id=identity.user.id, context={"client_category": "management"}, change_summary={"field_names": [exc.field] if exc.field else []})
        return list_page(request, db, settings, identity, error=str(exc), form_state=group_form_state("group_create", name=name, description=description, error=str(exc), field=exc.field), status_code=409 if exc.code == OutcomeCode.CONFLICT else 400)
    return RedirectResponse(f"/admin/groups/{result.group_id}", status_code=303)


@router.get("/{group_id}")
def show_group(
    group_id: int,
    request: Request,
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return detail_page(request, db, settings, identity, group_id)


@router.post("/{group_id}/profile")
def update_group_route(
    group_id: int,
    request: Request,
    expected_revision: int = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    confirm: bool = Form(False),
    csrf: str = Form(...),
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not valid_csrf(csrf, settings):
        error = "The form expired. Please try again."
        return detail_page(request, db, settings, identity, group_id, error=error, form_state=group_form_state("group_edit", name=name, description=description, expected_revision=expected_revision, record_id=group_id, error=error), status_code=400)
    try:
        result = update_group(db, identity.user, group_id, expected_revision, name=name, description=description, apply=confirm)
    except GroupValidationError as exc:
        record_event(db, "group_update_rejected", "denied" if exc.code == OutcomeCode.DENIED else "rejected", exc.code.value, actor_user_id=identity.user.id, target_group_id=group_id, context={"client_category": "management"}, change_summary={"revision": expected_revision, "field_names": [exc.field] if exc.field else []})
        return detail_page(request, db, settings, identity, group_id, error=str(exc), form_state=group_form_state("group_edit", name=name, description=description, expected_revision=expected_revision, record_id=group_id, error=str(exc), field=exc.field), status_code=409 if exc.code == OutcomeCode.CONFLICT else 403 if exc.code == OutcomeCode.DENIED else 400)
    return detail_page(request, db, settings, identity, group_id, preview=result if not confirm else None, message=result.message if confirm else None)


@router.post("/{group_id}/lifecycle")
def lifecycle_route(
    group_id: int,
    request: Request,
    action: str = Form(...),
    expected_revision: int = Form(...),
    confirm: bool = Form(False),
    csrf: str = Form(...),
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not valid_csrf(csrf, settings):
        return detail_page(request, db, settings, identity, group_id, error="The form expired. Please try again.", status_code=400)
    if action not in {"deactivate", "reactivate", "remove"}:
        return detail_page(request, db, settings, identity, group_id, error="Invalid group lifecycle action", status_code=400)
    try:
        if action == "deactivate":
            result = deactivate_group(db, identity.user, group_id, expected_revision, apply=confirm)
        elif action == "reactivate":
            result = reactivate_group(db, identity.user, group_id, expected_revision, apply=confirm)
        else:
            result = remove_group(db, identity.user, group_id, expected_revision, apply=confirm)
    except GroupValidationError as exc:
        record_event(db, "group_lifecycle_rejected", "denied" if exc.code == OutcomeCode.DENIED else "rejected", exc.code.value, actor_user_id=identity.user.id, target_group_id=group_id, context={"client_category": "management"}, change_summary={"revision": expected_revision, "action": action})
        status_code = 409 if exc.code == OutcomeCode.CONFLICT else 403 if exc.code == OutcomeCode.DENIED else 400
        return detail_page(request, db, settings, identity, group_id, error=str(exc), status_code=status_code)
    if confirm and action == "remove" and result.outcome == OutcomeCode.SUCCESS:
        return list_page(request, db, settings, identity, message=result.message)
    return detail_page(request, db, settings, identity, group_id, preview=result if not confirm else None, message=result.message if confirm else None)
