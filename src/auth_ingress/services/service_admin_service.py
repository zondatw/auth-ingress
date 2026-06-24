from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from auth_ingress.models import AccessRule, Group, ServiceEntry

SLUG = re.compile(r"^[a-z0-9-]+$")


class ServiceValidationError(ValueError):
    pass


def validate_destination(destination: str) -> str:
    parsed = urlsplit(destination.strip())
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ServiceValidationError("Destination must not contain credentials, query parameters, or fragments")
    if parsed.scheme == "mock" and parsed.netloc:
        return destination.strip()
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ServiceValidationError("Destination must be an internal HTTP(S) or mock URL")
    hostname = parsed.hostname.casefold()
    internal = hostname in {"localhost", "127.0.0.1", "::1"} or hostname.endswith(".internal")
    try:
        internal = internal or ipaddress.ip_address(hostname).is_private
    except ValueError:
        pass
    if not internal:
        raise ServiceValidationError("Destination must resolve through a trusted internal path")
    return destination.strip()


def save_service(
    db: Session,
    *,
    original_slug: str | None,
    slug: str,
    display_name: str,
    description: str,
    destination: str,
    status: str,
    group_names: list[str],
    proxy_enabled: bool = False,
    websocket_enabled: bool = False,
) -> tuple[ServiceEntry, str]:
    slug = slug.strip()
    if not SLUG.fullmatch(slug):
        raise ServiceValidationError("Slug must contain lowercase letters, numbers, and hyphens")
    if not display_name.strip():
        raise ServiceValidationError("Display name is required")
    if status not in {"enabled", "disabled"}:
        raise ServiceValidationError("Invalid status")
    if websocket_enabled and not proxy_enabled:
        raise ServiceValidationError("WebSockets require full proxy mode")
    destination = validate_destination(destination)
    names = sorted({name.strip() for name in group_names if name.strip()})
    if status == "enabled" and not names:
        raise ServiceValidationError("Enabled services require at least one access group")
    groups = list(db.scalars(select(Group).where(Group.name.in_(names))).all()) if names else []
    if len(groups) != len(names):
        raise ServiceValidationError("One or more groups do not exist")
    service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == original_slug)) if original_slug else None
    action = "updated" if service else "created"
    if service is None:
        if db.scalar(select(ServiceEntry).where(ServiceEntry.slug == slug)):
            raise ServiceValidationError("Slug already exists")
        service = ServiceEntry(slug=slug)
        db.add(service)
    elif slug != original_slug and db.scalar(select(ServiceEntry).where(ServiceEntry.slug == slug)):
        raise ServiceValidationError("Slug already exists")
    previous_status = service.status
    proxy_policy_changed = (
        service.destination != destination
        or service.proxy_enabled != proxy_enabled
        or service.websocket_enabled != websocket_enabled
    )
    service.slug = slug
    service.display_name = display_name.strip()
    service.description = description.strip() or None
    service.destination = destination
    service.status = status
    if proxy_policy_changed:
        service.compatibility_status = "unchecked"
        service.compatibility_checked_at = None
        service.compatibility_summary = None
    service.proxy_enabled = proxy_enabled
    service.websocket_enabled = websocket_enabled
    service.external_redirect_policy = "deny"
    db.flush()
    db.execute(delete(AccessRule).where(AccessRule.service_entry_id == service.id))
    db.add_all(AccessRule(service_entry_id=service.id, group_id=group.id) for group in groups)
    db.commit()
    if previous_status == "enabled" and status == "disabled":
        action = "disabled"
    return service, action
