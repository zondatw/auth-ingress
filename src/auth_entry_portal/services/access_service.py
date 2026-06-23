from collections import defaultdict

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from auth_entry_portal.models import AccessRule, Group, GroupMembership, ServiceEntry, User


def permitted_service_query(user: User):
    membership = exists().where(
        GroupMembership.user_id == user.id,
        GroupMembership.group_id == AccessRule.group_id,
    )
    return (
        select(ServiceEntry)
        .join(AccessRule, AccessRule.service_entry_id == ServiceEntry.id)
        .where(ServiceEntry.status == "enabled", membership)
        .distinct()
        .order_by(ServiceEntry.display_name)
    )


def list_permitted_services(db: Session, user: User) -> list[ServiceEntry]:
    if user.status != "active":
        return []
    return list(db.scalars(permitted_service_query(user)).all())


def may_enter(db: Session, user: User, service: ServiceEntry) -> bool:
    if user.status != "active" or service.status != "enabled":
        return False
    return bool(
        db.scalar(
            select(exists().where(
                AccessRule.service_entry_id == service.id,
                GroupMembership.user_id == user.id,
                GroupMembership.group_id == AccessRule.group_id,
            ))
        )
    )


def effective_access_for_user(db: Session, user: User) -> list[dict]:
    grants: dict[int, list[str]] = defaultdict(list)
    rows = db.execute(
        select(AccessRule.service_entry_id, Group.name)
        .join(Group, Group.id == AccessRule.group_id)
        .join(GroupMembership, GroupMembership.group_id == AccessRule.group_id)
        .where(GroupMembership.user_id == user.id)
        .order_by(Group.name)
    )
    for service_id, group_name in rows:
        grants[service_id].append(group_name)
    results = []
    for service in db.scalars(select(ServiceEntry).order_by(ServiceEntry.display_name, ServiceEntry.id)):
        groups = sorted(set(grants.get(service.id, [])))
        policy_granted = bool(groups)
        usable = policy_granted and user.status == "active" and service.status == "enabled"
        reason = None if usable else "user_disabled" if user.status != "active" else "service_disabled" if service.status != "enabled" else "no_matching_group"
        results.append({"service_id": service.id, "service_slug": service.slug, "display_name": service.display_name, "service_status": service.status, "granting_groups": groups, "policy_granted": policy_granted, "currently_usable": usable, "denial_reason": reason})
    return results
