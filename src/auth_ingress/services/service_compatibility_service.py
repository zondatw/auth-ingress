from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

import httpx
from sqlalchemy.orm import Session

from auth_ingress.config import Settings
from auth_ingress.models import ServiceEntry
from auth_ingress.security.proxy_destination import UnsafeDestination, resolve_destination
from auth_ingress.services.downstream_service import pooled_client
from auth_ingress.services.proxy_header_policy import UnsafeRedirect, rewrite_location

ABSOLUTE_REFERENCE = re.compile(r"(?:href|src)=[\"']https?://", re.IGNORECASE)


async def check_service_compatibility(db: Session, service: ServiceEntry, settings: Settings) -> tuple[str, str]:
    reasons: list[str] = []
    status = "compatible"
    try:
        resolve_destination(service.destination, settings)
        response = await pooled_client(settings.downstream_timeout_seconds).get(service.destination, follow_redirects=False)
        if response.status_code >= 500:
            reasons.append("upstream_error")
            status = "failed"
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type and ABSOLUTE_REFERENCE.search(response.text[:262144]):
            reasons.append("absolute_origin_reference")
            status = "limited" if status == "compatible" else status
        if "location" in response.headers:
            try:
                rewrite_location(response.headers["location"], service.destination, "https://service.invalid")
            except UnsafeRedirect:
                reasons.append("external_redirect")
                status = "limited" if status == "compatible" else status
    except (UnsafeDestination, httpx.HTTPError, UnicodeError):
        reasons.append("unreachable_or_unsafe")
        status = "failed"
    if service.websocket_enabled:
        reasons.append("websocket_requires_runtime_check")
        if status == "compatible":
            status = "limited"
    service.compatibility_status = status
    service.compatibility_checked_at = datetime.now(timezone.utc)
    service.compatibility_summary = ",".join(reasons) or "basic_http_compatible"
    db.commit()
    return status, service.compatibility_summary
