from __future__ import annotations

import re
from urllib.parse import urlsplit

from auth_ingress.config import Settings

SERVICE_SLUG = re.compile(r"^[a-z0-9-]+$")


def split_authority(authority: str) -> tuple[str, int | None]:
    parsed = urlsplit(f"//{authority}")
    if parsed.username or parsed.password or not parsed.hostname:
        raise ValueError("invalid host")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid host") from exc
    return parsed.hostname.casefold().rstrip("."), port


def service_slug_from_host(host: str, settings: Settings) -> str | None:
    hostname, port = split_authority(host)
    base_hostname, base_port = split_authority(settings.proxy_base_domain)
    if port != base_port:
        return None
    suffix = f".{base_hostname}"
    if not hostname.endswith(suffix):
        return None
    slug = hostname[: -len(suffix)]
    return slug if SERVICE_SLUG.fullmatch(slug) else None


def service_authority(slug: str, settings: Settings) -> str:
    if not SERVICE_SLUG.fullmatch(slug):
        raise ValueError("invalid service slug")
    hostname, port = split_authority(settings.proxy_base_domain)
    return f"{slug}.{hostname}{f':{port}' if port is not None else ''}"


def service_origin(slug: str, settings: Settings) -> str:
    if settings.proxy_scheme not in {"http", "https"}:
        raise ValueError("invalid proxy scheme")
    return f"{settings.proxy_scheme}://{service_authority(slug, settings)}"


def portal_origin(settings: Settings) -> str:
    scheme = settings.proxy_scheme
    split_authority(settings.portal_host)
    return f"{scheme}://{settings.portal_host}"
