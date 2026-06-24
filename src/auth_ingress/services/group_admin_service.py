from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_ingress.models import AccessRule, AuditEvent, Group, GroupMembership, ServiceEntry, User
from auth_ingress.services.audit_service import record_event
from auth_ingress.services.user_admin_service import require_admin_actor
from auth_ingress.services.user_management_types import OutcomeCode


class GroupValidationError(RuntimeError):
    def __init__(self, code: OutcomeCode, message: str, *, field: str | None = None):
        super().__init__(message)
        self.code = code
        self.field = field


@dataclass(slots=True)
class GroupDependencySummary:
    user_count: int = 0
    service_count: int = 0
    sample_users: list[User] = field(default_factory=list)
    sample_services: list[ServiceEntry] = field(default_factory=list)
    has_more_users: bool = False
    has_more_services: bool = False


@dataclass(slots=True)
class GroupOperationResult:
    operation: str
    outcome: OutcomeCode
    group_id: int | None = None
    revision: int | None = None
    changes: dict = field(default_factory=dict)
    dependency_summary: GroupDependencySummary | None = None
    message: str = ""


def normalize_group_name(name: str) -> str:
    return " ".join(name.strip().split())


def validate_group_name(name: str) -> tuple[str, str]:
    canonical = normalize_group_name(name)
    if not canonical:
        raise GroupValidationError(OutcomeCode.INVALID_INPUT, "Group name is required", field="name")
    if len(canonical) > 100:
        raise GroupValidationError(OutcomeCode.INVALID_INPUT, "Group name must be 100 characters or fewer", field="name")
    return canonical, canonical.casefold()


def _group(db: Session, group_id: int) -> Group:
    group = db.scalar(select(Group).where(Group.id == group_id).execution_options(populate_existing=True))
    if group is None:
        raise GroupValidationError(OutcomeCode.NOT_FOUND, "Group not found")
    return group


def _check_revision(group: Group, expected_revision: int) -> None:
    if group.revision != expected_revision:
        raise GroupValidationError(OutcomeCode.CONFLICT, "Group changed; refresh and try again")


def _record_group_event(
    db: Session,
    event_type: str,
    decision: str,
    reason: str,
    *,
    actor_id: int | None,
    group_id: int | None,
    changes: dict | None = None,
    commit: bool = False,
) -> None:
    record_event(
        db,
        event_type,
        decision,
        reason,
        actor_user_id=actor_id,
        target_group_id=group_id,
        context={"client_category": "management"},
        change_summary=changes or {},
        commit=commit,
    )


def dependency_summary(db: Session, group: Group, *, limit: int = 10) -> GroupDependencySummary:
    user_count = db.scalar(select(func.count()).select_from(GroupMembership).where(GroupMembership.group_id == group.id)) or 0
    service_count = db.scalar(select(func.count()).select_from(AccessRule).where(AccessRule.group_id == group.id)) or 0
    sample_users = list(
        db.scalars(
            select(User)
            .join(GroupMembership, GroupMembership.user_id == User.id)
            .where(GroupMembership.group_id == group.id)
            .order_by(User.normalized_email, User.id)
            .limit(limit)
        ).all()
    )
    sample_services = list(
        db.scalars(
            select(ServiceEntry)
            .join(AccessRule, AccessRule.service_entry_id == ServiceEntry.id)
            .where(AccessRule.group_id == group.id)
            .order_by(ServiceEntry.display_name, ServiceEntry.id)
            .limit(limit)
        ).all()
    )
    return GroupDependencySummary(
        user_count=user_count,
        service_count=service_count,
        sample_users=sample_users,
        sample_services=sample_services,
        has_more_users=user_count > len(sample_users),
        has_more_services=service_count > len(sample_services),
    )


def search_groups(db: Session, *, query: str = "", status: str | None = None, usage: str | None = None, page: int = 1, page_size: int = 100) -> list[dict]:
    page = max(page, 1)
    page_size = min(100, max(1, page_size))
    user_counts = select(GroupMembership.group_id, func.count(GroupMembership.id).label("user_count")).group_by(GroupMembership.group_id).subquery()
    service_counts = select(AccessRule.group_id, func.count(AccessRule.id).label("service_count")).group_by(AccessRule.group_id).subquery()
    statement = (
        select(Group, func.coalesce(user_counts.c.user_count, 0), func.coalesce(service_counts.c.service_count, 0))
        .outerjoin(user_counts, user_counts.c.group_id == Group.id)
        .outerjoin(service_counts, service_counts.c.group_id == Group.id)
    )
    if query.strip():
        needle = f"%{query.strip().casefold()}%"
        statement = statement.where(or_(Group.normalized_name.like(needle), func.lower(Group.description).like(needle)))
    if status in {"active", "deactivated"}:
        statement = statement.where(Group.status == status)
    if usage == "unused":
        statement = statement.where(func.coalesce(user_counts.c.user_count, 0) == 0, func.coalesce(service_counts.c.service_count, 0) == 0)
    elif usage == "used":
        statement = statement.where(or_(func.coalesce(user_counts.c.user_count, 0) > 0, func.coalesce(service_counts.c.service_count, 0) > 0))
    rows = db.execute(statement.order_by(Group.normalized_name, Group.id).offset((page - 1) * page_size).limit(page_size)).all()
    return [{"group": group, "user_count": user_count, "service_count": service_count} for group, user_count, service_count in rows]


def group_detail(db: Session, actor: User, group_id: int, *, audit: bool = True) -> dict:
    actor = require_admin_actor(db, actor)
    group = _group(db, group_id)
    summary = dependency_summary(db, group)
    events = list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.target_group_id == group.id)
            .order_by(AuditEvent.created_at.desc())
            .limit(10)
        ).all()
    )
    if audit:
        _record_group_event(db, "group_viewed", "allowed", "admin_view", actor_id=actor.id, group_id=group.id, commit=True)
    return {"group": group, "dependencies": summary, "events": events}


def create_group(db: Session, actor: User, name: str, description: str = "", *, apply: bool = True) -> GroupOperationResult:
    actor = require_admin_actor(db, actor)
    canonical, normalized = validate_group_name(name)
    description = description.strip()[:500] if description else ""
    if db.scalar(select(Group.id).where(Group.normalized_name == normalized)):
        raise GroupValidationError(OutcomeCode.INVALID_INPUT, "Group name is already in use", field="name")
    changes = {"field_names": ["name", "description"]}
    if not apply:
        return GroupOperationResult("group_create", OutcomeCode.SUCCESS, changes=changes, message="Preview group creation")
    try:
        group = Group(name=canonical, description=description or None)
        db.add(group)
        db.flush()
        _record_group_event(db, "group_created", "changed", "created", actor_id=actor.id, group_id=group.id, changes={"revision": group.revision, **changes})
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise GroupValidationError(OutcomeCode.CONFLICT, "Group name is already in use", field="name") from error
    return GroupOperationResult("group_create", OutcomeCode.SUCCESS, group.id, group.revision, changes=changes, message="Group created")


def preview_update_group(db: Session, actor: User, group_id: int, expected_revision: int, *, name: str, description: str = "") -> GroupOperationResult:
    return update_group(db, actor, group_id, expected_revision, name=name, description=description, apply=False)


def update_group(db: Session, actor: User, group_id: int, expected_revision: int, *, name: str, description: str = "", apply: bool) -> GroupOperationResult:
    actor = require_admin_actor(db, actor)
    group = _group(db, group_id)
    _check_revision(group, expected_revision)
    canonical, normalized = validate_group_name(name)
    duplicate = db.scalar(select(Group.id).where(Group.normalized_name == normalized, Group.id != group.id))
    if duplicate:
        raise GroupValidationError(OutcomeCode.INVALID_INPUT, "Group name is already in use", field="name")
    description = description.strip()[:500] if description else ""
    requested = {}
    if canonical != group.name:
        requested["name"] = canonical
    if (description or None) != group.description:
        requested["description"] = description
    if not requested:
        return GroupOperationResult("group_update", OutcomeCode.NO_CHANGE, group.id, group.revision, message="Group already matches")
    changes = {"field_names": sorted(requested)}
    if not apply:
        return GroupOperationResult("group_update", OutcomeCode.SUCCESS, group.id, group.revision, changes={**changes, "name": canonical, "description": description}, message="Preview group changes")
    for key, value in requested.items():
        setattr(group, key, value or None if key == "description" else value)
    group.revision += 1
    _record_group_event(db, "group_updated", "changed", "updated", actor_id=actor.id, group_id=group.id, changes={"revision": group.revision, **changes})
    db.commit()
    return GroupOperationResult("group_update", OutcomeCode.SUCCESS, group.id, group.revision, changes=changes, message="Group updated")


def lifecycle_preview(db: Session, actor: User, group_id: int, expected_revision: int, action: str) -> GroupOperationResult:
    actor = require_admin_actor(db, actor)
    group = _group(db, group_id)
    _check_revision(group, expected_revision)
    summary = dependency_summary(db, group)
    return GroupOperationResult(f"group_{action}", OutcomeCode.SUCCESS, group.id, group.revision, dependency_summary=summary, changes={"action": action}, message=f"Preview group {action}")


def _protect_last_admin_group_change(db: Session, group: Group) -> None:
    active_admin_ids = set(db.scalars(select(User.id).where(User.is_admin.is_(True), User.status == "active")).all())
    if not active_admin_ids:
        raise GroupValidationError(OutcomeCode.DENIED, "The last active administrator cannot be put at risk")
    member_admin_ids = set(
        db.scalars(
            select(User.id)
            .join(GroupMembership, GroupMembership.user_id == User.id)
            .where(GroupMembership.group_id == group.id, User.is_admin.is_(True), User.status == "active")
        ).all()
    )
    if active_admin_ids and active_admin_ids == member_admin_ids:
        raise GroupValidationError(OutcomeCode.DENIED, "The last active administrator group cannot be deactivated or removed")


def deactivate_group(db: Session, actor: User, group_id: int, expected_revision: int, *, apply: bool) -> GroupOperationResult:
    actor = require_admin_actor(db, actor)
    group = _group(db, group_id)
    _check_revision(group, expected_revision)
    if group.status == "deactivated":
        return GroupOperationResult("group_deactivate", OutcomeCode.NO_CHANGE, group.id, group.revision, message="Group is already deactivated")
    _protect_last_admin_group_change(db, group)
    summary = dependency_summary(db, group)
    if not apply:
        return GroupOperationResult("group_deactivate", OutcomeCode.SUCCESS, group.id, group.revision, dependency_summary=summary, changes={"action": "deactivate"}, message="Preview group deactivation")
    group.status = "deactivated"
    group.revision += 1
    _record_group_event(db, "group_deactivated", "changed", "deactivated", actor_id=actor.id, group_id=group.id, changes={"revision": group.revision, "action": "deactivate", "user_count": summary.user_count, "service_count": summary.service_count})
    db.commit()
    return GroupOperationResult("group_deactivate", OutcomeCode.SUCCESS, group.id, group.revision, dependency_summary=summary, message="Group deactivated")


def reactivate_group(db: Session, actor: User, group_id: int, expected_revision: int, *, apply: bool) -> GroupOperationResult:
    actor = require_admin_actor(db, actor)
    group = _group(db, group_id)
    _check_revision(group, expected_revision)
    if group.status == "active":
        return GroupOperationResult("group_reactivate", OutcomeCode.NO_CHANGE, group.id, group.revision, message="Group is already active")
    summary = dependency_summary(db, group)
    if not apply:
        return GroupOperationResult("group_reactivate", OutcomeCode.SUCCESS, group.id, group.revision, dependency_summary=summary, changes={"action": "reactivate"}, message="Preview group reactivation")
    group.status = "active"
    group.revision += 1
    _record_group_event(db, "group_reactivated", "changed", "reactivated", actor_id=actor.id, group_id=group.id, changes={"revision": group.revision, "action": "reactivate", "user_count": summary.user_count, "service_count": summary.service_count})
    db.commit()
    return GroupOperationResult("group_reactivate", OutcomeCode.SUCCESS, group.id, group.revision, dependency_summary=summary, message="Group reactivated")


def remove_group(db: Session, actor: User, group_id: int, expected_revision: int, *, apply: bool) -> GroupOperationResult:
    actor = require_admin_actor(db, actor)
    group = _group(db, group_id)
    _check_revision(group, expected_revision)
    _protect_last_admin_group_change(db, group)
    summary = dependency_summary(db, group)
    if summary.user_count or summary.service_count:
        _record_group_event(db, "group_remove_blocked", "denied", "dependencies", actor_id=actor.id, group_id=group.id, changes={"user_count": summary.user_count, "service_count": summary.service_count}, commit=True)
        raise GroupValidationError(OutcomeCode.CONFLICT, "Group still has users or services; clear dependencies before removal")
    if not apply:
        return GroupOperationResult("group_remove", OutcomeCode.SUCCESS, group.id, group.revision, dependency_summary=summary, changes={"action": "remove"}, message="Preview group removal")
    group_id_value = group.id
    _record_group_event(db, "group_removed", "changed", "removed", actor_id=actor.id, group_id=group_id_value, changes={"revision": group.revision, "action": "remove"})
    db.execute(delete(Group).where(Group.id == group_id_value))
    db.commit()
    return GroupOperationResult("group_remove", OutcomeCode.SUCCESS, group_id_value, changes={"action": "remove"}, message="Group removed")
