from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from auth_portal.models import AccessRule, GroupMembership, ServiceEntry, User


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

