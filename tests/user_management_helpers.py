from __future__ import annotations

from sqlalchemy.orm import Session

from auth_entry_portal.models import AccessRule, Group, GroupMembership, ServiceEntry, User
from auth_entry_portal.security.passwords import hash_password


def managed_user(db: Session, email: str, *, admin: bool = False, status: str = "active") -> User:
    user = User(
        email=email,
        normalized_email=email.strip().casefold(),
        display_name=email.split("@", 1)[0].title(),
        password_hash=hash_password("correct-password"),
        status=status,
        is_admin=admin,
    )
    db.add(user)
    db.flush()
    return user


def granting_group(db: Session, name: str, service: ServiceEntry, *users: User) -> Group:
    group = Group(name=name, description=name)
    db.add(group)
    db.flush()
    db.add(AccessRule(service_entry_id=service.id, group_id=group.id))
    db.add_all(GroupMembership(user_id=user.id, group_id=group.id) for user in users)
    db.flush()
    return group
