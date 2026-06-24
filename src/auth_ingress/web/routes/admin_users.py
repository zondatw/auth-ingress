from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_ingress.config import Settings, get_settings
from auth_ingress.models import Group
from auth_ingress.repositories.database import get_db
from auth_ingress.security.csrf import valid_csrf
from auth_ingress.security.dependencies import Identity, require_admin
from auth_ingress.security.rate_limit import ManagementRequestLimiter
from auth_ingress.services.password_reset_service import initiate_reset
from auth_ingress.services.recovery_delivery import SMTPRecoveryDelivery
from auth_ingress.services.user_admin_service import change_memberships, create_user, delete_user, search_users, set_user_status, update_user, user_detail
from auth_ingress.services.user_management_types import ManagementError, OutcomeCode
from auth_ingress.web.web import template

router = APIRouter(prefix="/admin/users")
creation_router = APIRouter(prefix="/admin/users")
_limiters: dict[tuple[int, int], ManagementRequestLimiter] = {}


def limiter(settings: Settings) -> ManagementRequestLimiter:
    key = (settings.management_rate_limit_attempts, settings.management_rate_limit_window_seconds)
    return _limiters.setdefault(key, ManagementRequestLimiter(*key))


def _groups(db: Session) -> list[Group]:
    return list(db.scalars(select(Group).order_by(Group.name)).all())


def detail_page(request: Request, db: Session, settings: Settings, identity: Identity, user_id: int, *, preview=None, error=None, message=None, status_code=200):
    try:
        detail = user_detail(db, identity.user, user_id, audit=preview is None and error is None)
    except ManagementError as exc:
        return template(request, "errors/access_denied.html", settings, title="User not found", message=str(exc), status_code=404)
    return template(request, "admin/user_detail.html", settings, user=identity.user, managed=detail["user"], memberships=detail["memberships"], effective_access=detail["effective_access"], groups=_groups(db), preview=preview, error=error, message=message, status_code=status_code)


@router.get("")
def list_users(request: Request, q: str = "", status: str | None = None, admin: str | None = None, group: str | None = None, page: int = 1, identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if page < 1 or status not in {None, "", "active", "disabled"} or admin not in {None, "", "true", "false"}:
        return template(request, "admin/users.html", settings, user=identity.user, users=[], groups=_groups(db), page=1, filters={}, error="Invalid search filters", status_code=400)
    if not limiter(settings).allow(f"user:{identity.user.id}"):
        return template(request, "errors/access_denied.html", settings, title="Too many requests", message="Wait and try again.", status_code=429)
    users = search_users(db, query=q, status=status or None, is_admin=None if not admin else admin == "true", group=group or None, page=page, page_size=settings.user_search_page_size)
    return template(request, "admin/users.html", settings, user=identity.user, users=users, groups=_groups(db), page=page, filters={"q": q, "status": status or "", "admin": admin or "", "group": group or ""}, error=None, create_preview=None, message=None)


@router.get("/{user_id}")
def show_user(user_id: int, request: Request, identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    return detail_page(request, db, settings, identity, user_id)


@router.post("/{user_id}/memberships")
def memberships(user_id: int, request: Request, expected_revision: int = Form(...), group_ids: list[int] = Form(default=[]), confirm: bool = Form(False), csrf: str = Form(...), identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if not valid_csrf(csrf, settings):
        return detail_page(request, db, settings, identity, user_id, error="The form expired. Please try again.", status_code=400)
    if not limiter(settings).allow(f"mutation:{identity.user.id}"):
        return detail_page(request, db, settings, identity, user_id, error="Too many requests. Wait and try again.", status_code=429)
    try:
        result = change_memberships(db, identity.user, user_id, set(group_ids), expected_revision, apply=confirm)
    except ManagementError as exc:
        status_code = {OutcomeCode.INVALID_INPUT: 400, OutcomeCode.DENIED: 403, OutcomeCode.NOT_FOUND: 404, OutcomeCode.CONFLICT: 409}.get(exc.code, 400)
        return detail_page(request, db, settings, identity, user_id, error=str(exc), status_code=status_code)
    return detail_page(request, db, settings, identity, user_id, preview=None if confirm else result, message=result.message if confirm else None)


def _list_after_create(request: Request, db: Session, settings: Settings, identity: Identity, *, preview=None, error=None, message=None, temporary_password=None, status_code=200):
    return template(request, "admin/users.html", settings, user=identity.user, users=search_users(db, page_size=settings.user_search_page_size), groups=_groups(db), page=1, filters={"q": "", "status": "", "admin": "", "group": ""}, error=error, create_preview=preview, message=message, temporary_password=temporary_password, status_code=status_code)


async def _create_user(request: Request, email: str, display_name: str, status: str, is_admin: bool, group_ids: list[int], confirm: bool, csrf: str, identity: Identity, db: Session, settings: Settings):
    if not valid_csrf(csrf, settings):
        return _list_after_create(request, db, settings, identity, error="The form expired. Please try again.", status_code=400)
    try:
        result = create_user(db, identity.user, email, display_name, status, is_admin, set(group_ids), apply=confirm, settings=settings, delivery=SMTPRecoveryDelivery(settings), base_url=str(request.base_url).rstrip("/"))
    except ManagementError as exc:
        return _list_after_create(request, db, settings, identity, error=str(exc), status_code=400 if exc.code == OutcomeCode.INVALID_INPUT else 409)
    return _list_after_create(request, db, settings, identity, preview=None if confirm else {"result": result, "email": email, "display_name": display_name, "status": status, "is_admin": is_admin, "group_ids": group_ids}, message=result.message if confirm else None, temporary_password=result.temporary_password if confirm else None, status_code=201 if confirm else 200)


@creation_router.post("/preview")
async def preview_create(request: Request, email: str = Form(...), display_name: str = Form(...), status: str = Form("active"), is_admin: bool = Form(False), group_ids: list[int] = Form(default=[]), confirm: bool = Form(False), csrf: str = Form(...), identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    return await _create_user(request, email, display_name, status, is_admin, group_ids, confirm, csrf, identity, db, settings)


@creation_router.post("/confirm")
async def confirm_create(request: Request, email: str = Form(...), display_name: str = Form(...), status: str = Form("active"), is_admin: bool = Form(False), group_ids: list[int] = Form(default=[]), csrf: str = Form(...), identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    return await _create_user(request, email, display_name, status, is_admin, group_ids, True, csrf, identity, db, settings)


@router.post("/{user_id}/profile")
def profile(user_id: int, request: Request, expected_revision: int = Form(...), email: str = Form(...), display_name: str = Form(...), is_admin: bool = Form(False), confirm: bool = Form(False), csrf: str = Form(...), identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if not valid_csrf(csrf, settings): return detail_page(request, db, settings, identity, user_id, error="The form expired. Please try again.", status_code=400)
    try: result = update_user(db, identity.user, user_id, expected_revision, email=email, display_name=display_name, is_admin=is_admin, apply=confirm)
    except ManagementError as exc: return detail_page(request, db, settings, identity, user_id, error=str(exc), status_code=403 if exc.code == OutcomeCode.DENIED else 409 if exc.code == OutcomeCode.CONFLICT else 400)
    return detail_page(request, db, settings, identity, user_id, preview=result if not confirm else None, message=result.message if confirm else None)


@router.post("/{user_id}/status")
def status_change(user_id: int, request: Request, expected_revision: int = Form(...), status: str = Form(...), confirm: bool = Form(False), csrf: str = Form(...), identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if not valid_csrf(csrf, settings): return detail_page(request, db, settings, identity, user_id, error="The form expired. Please try again.", status_code=400)
    try: result = set_user_status(db, identity.user, user_id, expected_revision, status, apply=confirm)
    except ManagementError as exc: return detail_page(request, db, settings, identity, user_id, error=str(exc), status_code=403 if exc.code == OutcomeCode.DENIED else 409 if exc.code == OutcomeCode.CONFLICT else 400)
    return detail_page(request, db, settings, identity, user_id, preview=result if not confirm else None, message=result.message if confirm else None)


@router.post("/{user_id}/delete")
def delete_account(user_id: int, request: Request, expected_revision: int = Form(...), confirm: bool = Form(False), csrf: str = Form(...), identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if not valid_csrf(csrf, settings): return detail_page(request, db, settings, identity, user_id, error="The form expired. Please try again.", status_code=400)
    try: result = delete_user(db, identity.user, user_id, expected_revision, apply=confirm)
    except ManagementError as exc: return detail_page(request, db, settings, identity, user_id, error=str(exc), status_code=403 if exc.code == OutcomeCode.DENIED else 409 if exc.code == OutcomeCode.CONFLICT else 400)
    if confirm:
        return _list_after_create(request, db, settings, identity, message=result.message)
    return detail_page(request, db, settings, identity, user_id, preview=result)


@router.post("/{user_id}/reset-password")
def reset_password(user_id: int, request: Request, expected_revision: int = Form(...), confirm: bool = Form(False), csrf: str = Form(...), identity: Identity = Depends(require_admin), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if not valid_csrf(csrf, settings): return detail_page(request, db, settings, identity, user_id, error="The form expired. Please try again.", status_code=400)
    try:
        actor = __import__("auth_ingress.services.user_admin_service", fromlist=["require_admin_actor"]).require_admin_actor(db, identity.user)
        target = db.get(__import__("auth_ingress.models", fromlist=["User"]).User, user_id)
        if target is None: raise ManagementError(OutcomeCode.NOT_FOUND, "User not found")
        if target.revision != expected_revision: raise ManagementError(OutcomeCode.CONFLICT, "User changed; refresh and try again")
        if not confirm:
            result = __import__("auth_ingress.services.user_management_types", fromlist=["OperationResult"]).OperationResult("password_reset", OutcomeCode.SUCCESS, target.id, target.revision, message="Preview password reset")
            return detail_page(request, db, settings, identity, user_id, preview=result)
        initiate_reset(db, actor, target, settings, SMTPRecoveryDelivery(settings), str(request.base_url).rstrip("/"))
        return detail_page(request, db, settings, identity, user_id, message="Password reset sent")
    except ManagementError as exc:
        return detail_page(request, db, settings, identity, user_id, error=str(exc), status_code=503 if exc.code == OutcomeCode.DEPENDENCY_FAILURE else 409 if exc.code == OutcomeCode.CONFLICT else 400)
