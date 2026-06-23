from __future__ import annotations

import secrets

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from auth_entry_portal.models import Group, GroupMembership, User
from auth_entry_portal.services.access_service import effective_access_for_user
from auth_entry_portal.services.audit_service import record_event
from auth_entry_portal.security.passwords import hash_password
from auth_entry_portal.services.recovery_delivery import RecoveryDelivery
from auth_entry_portal.services.session_service import revoke_user_sessions
from auth_entry_portal.services.user_management_types import ManagementError, OperationResult, OutcomeCode


def require_admin_actor(db: Session, actor: User) -> User:
    current = db.scalar(select(User).where(User.id == actor.id).execution_options(populate_existing=True))
    if current is None or current.status != "active" or current.credential_status != "active" or not current.is_admin:
        raise ManagementError(OutcomeCode.DENIED, "Administrator access required")
    return current


def search_users(db: Session, *, query: str = "", status: str | None = None, is_admin: bool | None = None, group: str | None = None, page: int = 1, page_size: int = 50) -> list[User]:
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    statement = select(User).options(selectinload(User.memberships).selectinload(GroupMembership.group))
    if query.strip():
        needle = f"%{query.strip().casefold()}%"
        statement = statement.where(or_(User.normalized_email.like(needle), func.lower(User.display_name).like(needle)))
    if status in {"active", "disabled"}:
        statement = statement.where(User.status == status)
    if is_admin is not None:
        statement = statement.where(User.is_admin.is_(is_admin))
    if group:
        statement = statement.join(GroupMembership).join(Group)
        statement = statement.where(Group.id == int(group)) if group.isdigit() else statement.where(Group.name == group)
    statement = statement.order_by(User.normalized_email, User.id).offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(statement).unique().all())


def user_detail(db: Session, actor: User, user_id: int, *, audit: bool = True) -> dict:
    actor = require_admin_actor(db, actor)
    user = db.scalar(select(User).where(User.id == user_id).options(selectinload(User.memberships).selectinload(GroupMembership.group)).execution_options(populate_existing=True))
    if user is None:
        raise ManagementError(OutcomeCode.NOT_FOUND, "User not found")
    if audit:
        record_event(db, "user_viewed", "allowed", "admin_view", actor_user_id=actor.id, target_user_id=user.id, context={"client_category": "browser"})
    return {"user": user, "memberships": sorted((membership.group for membership in user.memberships), key=lambda item: item.name), "effective_access": effective_access_for_user(db, user)}


def change_memberships(db: Session, actor: User, target_user_id: int, desired_group_ids: set[int], expected_revision: int, *, apply: bool, client_category: str = "browser") -> OperationResult:
    actor = require_admin_actor(db, actor)
    target = db.scalar(select(User).where(User.id == target_user_id).options(selectinload(User.memberships)).execution_options(populate_existing=True))
    if target is None:
        raise ManagementError(OutcomeCode.NOT_FOUND, "User not found")
    if target.revision != expected_revision:
        raise ManagementError(OutcomeCode.CONFLICT, "User changed; refresh and preview again")
    groups = list(db.scalars(select(Group).where(Group.id.in_(desired_group_ids))).all()) if desired_group_ids else []
    if {group.id for group in groups} != desired_group_ids:
        raise ManagementError(OutcomeCode.INVALID_INPUT, "One or more groups do not exist")
    existing = {membership.group_id for membership in target.memberships}
    added, removed = sorted(desired_group_ids - existing), sorted(existing - desired_group_ids)
    if not added and not removed:
        return OperationResult("membership_set", OutcomeCode.NO_CHANGE, target.id, target.revision, message="Access list already matches")
    before = effective_access_for_user(db, target)
    changes = {"groups_added": added, "groups_removed": removed}
    if not apply:
        return OperationResult("membership_set", OutcomeCode.SUCCESS, target.id, target.revision, changes=changes, effective_access_changes=before, message="Preview changes")
    changed = db.execute(update(User).where(User.id == target.id, User.revision == expected_revision).values(revision=User.revision + 1))
    if not changed.rowcount:
        db.rollback()
        raise ManagementError(OutcomeCode.CONFLICT, "User changed; refresh and preview again")
    db.execute(delete(GroupMembership).where(GroupMembership.user_id == target.id))
    db.add_all(GroupMembership(user_id=target.id, group_id=group_id) for group_id in sorted(desired_group_ids))
    db.flush()
    db.expire(target)
    new_revision = target.revision
    after = effective_access_for_user(db, target)
    effective_changes = [item for item in after if next((old for old in before if old["service_id"] == item["service_id"]), None) != item]
    record_event(db, "membership_changed", "changed", "membership_set", actor_user_id=actor.id, target_user_id=target.id, context={"client_category": client_category}, change_summary={"revision": new_revision, **changes}, commit=False)
    db.commit()
    return OperationResult("membership_set", OutcomeCode.SUCCESS, target.id, new_revision, changes=changes, effective_access_changes=effective_changes, message="Access updated")


def create_user(db: Session, actor: User, email: str, display_name: str, status: str, is_admin: bool, group_ids: set[int], *, apply: bool, settings=None, delivery: RecoveryDelivery | None = None, base_url: str = "") -> OperationResult:
    actor = require_admin_actor(db, actor)
    _ = (settings, delivery, base_url)
    canonical_email, canonical_name = email.strip(), display_name.strip()
    if not canonical_name or "@" not in canonical_email or status not in {"active", "disabled"}:
        raise ManagementError(OutcomeCode.INVALID_INPUT, "Valid email, display name, and status are required")
    if db.scalar(select(User.id).where(User.normalized_email == canonical_email.casefold())):
        raise ManagementError(OutcomeCode.INVALID_INPUT, "Email is already in use")
    groups = list(db.scalars(select(Group).where(Group.id.in_(group_ids))).all()) if group_ids else []
    if {group.id for group in groups} != group_ids:
        raise ManagementError(OutcomeCode.INVALID_INPUT, "One or more groups do not exist")
    changes = {"field_names": ["email", "display_name", "status", "is_admin"], "groups_added": sorted(group_ids)}
    if not apply:
        return OperationResult("user_create", OutcomeCode.SUCCESS, changes=changes, message="Preview user creation")
    temporary_password = secrets.token_urlsafe(18)
    try:
        user = User(email=canonical_email, display_name=canonical_name, password_hash=hash_password(temporary_password), status=status, credential_status="temporary", is_admin=is_admin)
        db.add(user); db.flush()
        db.add_all(GroupMembership(user_id=user.id, group_id=group_id) for group_id in sorted(group_ids))
        record_event(db, "user_created", "changed", "created", actor_user_id=actor.id, target_user_id=user.id, context={"client_category": "management"}, change_summary={"revision": user.revision, **changes}, commit=False)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ManagementError(OutcomeCode.CONFLICT, "User identity changed concurrently") from error
    return OperationResult("user_create", OutcomeCode.SUCCESS, user.id, user.revision, changes=changes, message="User created; temporary password generated", temporary_password=temporary_password)


def _target_for_change(db: Session, actor: User, target_id: int, expected_revision: int) -> tuple[User, User]:
    actor = require_admin_actor(db, actor)
    target = db.scalar(select(User).where(User.id == target_id).execution_options(populate_existing=True))
    if target is None:
        raise ManagementError(OutcomeCode.NOT_FOUND, "User not found")
    if target.revision != expected_revision:
        raise ManagementError(OutcomeCode.CONFLICT, "User changed; refresh and preview again")
    return actor, target


def _protect_admin_change(db: Session, actor: User, target: User, *, removing_admin: bool = False, disabling: bool = False) -> None:
    if target.id == actor.id and (removing_admin or disabling):
        raise ManagementError(OutcomeCode.DENIED, "Administrators cannot disable or demote their own account")
    if target.is_admin and target.status == "active" and (removing_admin or disabling):
        others = db.scalar(select(func.count()).select_from(User).where(User.is_admin.is_(True), User.status == "active", User.id != target.id)) or 0
        if not others:
            raise ManagementError(OutcomeCode.DENIED, "The last active administrator cannot be disabled or demoted")


def update_user(db: Session, actor: User, target_id: int, expected_revision: int, *, email: str | None = None, display_name: str | None = None, is_admin: bool | None = None, apply: bool) -> OperationResult:
    actor, target = _target_for_change(db, actor, target_id, expected_revision)
    _protect_admin_change(db, actor, target, removing_admin=is_admin is False and target.is_admin)
    requested = {}
    if email is not None and email.strip() != target.email:
        if "@" not in email:
            raise ManagementError(OutcomeCode.INVALID_INPUT, "Valid email is required")
        requested["email"] = email.strip()
    if display_name is not None and display_name.strip() != target.display_name:
        if not display_name.strip():
            raise ManagementError(OutcomeCode.INVALID_INPUT, "Display name is required")
        requested["display_name"] = display_name.strip()
    if is_admin is not None and is_admin != target.is_admin:
        requested["is_admin"] = is_admin
    if not requested:
        return OperationResult("user_update", OutcomeCode.NO_CHANGE, target.id, target.revision, message="User already matches")
    final_values = {"email": requested.get("email", target.email), "display_name": requested.get("display_name", target.display_name), "is_admin": requested.get("is_admin", target.is_admin)}
    if not apply:
        return OperationResult("user_update", OutcomeCode.SUCCESS, target.id, target.revision, changes={"field_names": sorted(requested), **final_values}, message="Preview profile changes")
    try:
        for key, value in requested.items(): setattr(target, key, value)
        target.revision += 1
        if "is_admin" in requested:
            revoke_user_sessions(db, target.id)
        record_event(db, "user_updated", "changed", "profile_updated", actor_user_id=actor.id, target_user_id=target.id, context={"client_category": "management"}, change_summary={"revision": target.revision, "field_names": sorted(requested)}, commit=False)
        db.commit()
    except IntegrityError as error:
        db.rollback(); raise ManagementError(OutcomeCode.CONFLICT, "Email is already in use") from error
    return OperationResult("user_update", OutcomeCode.SUCCESS, target.id, target.revision, changes={"field_names": sorted(requested), **final_values}, message="Profile updated")


def set_user_status(db: Session, actor: User, target_id: int, expected_revision: int, status: str, *, apply: bool) -> OperationResult:
    if status not in {"active", "disabled"}:
        raise ManagementError(OutcomeCode.INVALID_INPUT, "Invalid status")
    actor, target = _target_for_change(db, actor, target_id, expected_revision)
    _protect_admin_change(db, actor, target, disabling=status == "disabled" and target.status == "active")
    if target.status == status:
        return OperationResult("user_status", OutcomeCode.NO_CHANGE, target.id, target.revision, message="Status already matches")
    if not apply:
        return OperationResult("user_status", OutcomeCode.SUCCESS, target.id, target.revision, changes={"status": status}, message="Preview status change")
    target.status = status; target.revision += 1
    if status == "disabled": revoke_user_sessions(db, target.id)
    record_event(db, "user_disabled" if status == "disabled" else "user_reactivated", "changed", status, actor_user_id=actor.id, target_user_id=target.id, context={"client_category": "management"}, change_summary={"revision": target.revision, "status": status}, commit=False)
    db.commit()
    return OperationResult("user_status", OutcomeCode.SUCCESS, target.id, target.revision, changes={"status": status}, message=f"Account {status}")
