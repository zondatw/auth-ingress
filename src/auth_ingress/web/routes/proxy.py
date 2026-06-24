from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import Request, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import select

from auth_ingress.config import Settings
from auth_ingress.models import ServiceEntry
from auth_ingress.security.cookies import encode_proxy_credential, proxy_cookie_options
from auth_ingress.security.proxy_host import portal_origin, service_slug_from_host, split_authority
from auth_ingress.services.audit_service import record_event
from auth_ingress.services.proxy_authorization_service import (
    ProxyAuthorizationError,
    authorize_proxy_cookie,
    consume_launch_ticket,
)
from auth_ingress.services.proxy_http_service import ProxyHTTPError, forward_http
from auth_ingress.services.proxy_websocket_service import ProxyWebSocketError, relay_websocket

logger = logging.getLogger("auth_portal")


def safe_error(title: str, message: str, status_code: int) -> HTMLResponse:
    return HTMLResponse(
        f"<!doctype html><html><head><meta name=viewport content='width=device-width'></head><body><main><h1>{title}</h1><p>{message}</p></main></body></html>",
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )


def _is_proxy_authority(host: str, settings: Settings) -> bool:
    try:
        hostname, port = split_authority(host)
        base_hostname, base_port = split_authority(settings.proxy_base_domain)
    except ValueError:
        return False
    return port == base_port and (hostname == base_hostname or hostname.endswith(f".{base_hostname}"))


class ProxyDispatchMiddleware:
    def __init__(self, app, settings: Settings, session_factory):
        self.app = app
        self.settings = settings
        self.session_factory = session_factory

    async def __call__(self, scope, receive, send):
        if scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return
        headers = {name.lower(): value for name, value in scope.get("headers", [])}
        host = headers.get(b"host", b"").decode("latin-1")
        if not _is_proxy_authority(host, self.settings):
            await self.app(scope, receive, send)
            return
        if scope["type"] == "websocket":
            await handle_proxy_websocket(scope, receive, send, host, self.settings, self.session_factory)
            return
        response = await handle_proxy_http(scope, receive, host, self.settings, self.session_factory)
        await response(scope, receive, send)


async def handle_proxy_http(scope, receive, host: str, settings: Settings, session_factory) -> Response:
    request = Request(scope, receive)
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))[:120]
    request.state.correlation_id = correlation_id
    try:
        slug = service_slug_from_host(host, settings)
    except ValueError:
        slug = None
    with session_factory() as db:
        service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == slug)) if slug else None
        if service is None:
            response = safe_error("Service not found", "This protected service is unavailable.", 404)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        if request.url.path == "/__portal/bootstrap":
            token = request.query_params.get("ticket", "")
            try:
                identity = consume_launch_ticket(db, token, service, settings)
            except ProxyAuthorizationError as exc:
                record_event(db, "proxy_launch_denied", "denied", exc.reason, service_entry_id=service.id, context={"correlation_id": correlation_id, "client_category": "browser"})
                return safe_error("Access denied", "This launch link is invalid or expired. Return to the portal.", 403)
            remaining = max(0, int((identity.session.expires_at.replace(tzinfo=identity.session.expires_at.tzinfo or timezone.utc) - datetime.now(timezone.utc)).total_seconds()))
            response = RedirectResponse("/", status_code=302, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
            response.set_cookie(
                settings.proxy_cookie_name,
                encode_proxy_credential(identity.session.id, service.id, identity.session.expires_at, settings),
                **proxy_cookie_options(settings, remaining),
            )
            record_event(db, "proxy_launch_consumed", "allowed", "ticket_consumed", actor_user_id=identity.user.id, service_entry_id=service.id, context={"correlation_id": correlation_id, "client_category": "browser"})
            return response
        if request.url.path.startswith("/__portal/"):
            return safe_error("Not found", "The requested resource does not exist.", 404)
        try:
            identity = authorize_proxy_cookie(db, request.cookies.get(settings.proxy_cookie_name), service, settings)
        except ProxyAuthorizationError as exc:
            record_event(db, "proxy_request_denied", "denied", exc.reason, service_entry_id=service.id, context={"correlation_id": correlation_id, "client_category": "browser"})
            response = RedirectResponse(f"{portal_origin(settings)}/services/{service.slug}", status_code=302, headers={"Cache-Control": "no-store"})
            response.delete_cookie(settings.proxy_cookie_name, path="/")
            return response
        try:
            response = await forward_http(request, service, settings)
        except ProxyHTTPError as exc:
            event = "proxy_redirect_denied" if exc.reason == "unsafe_redirect" else "proxy_upstream_unavailable"
            record_event(db, event, "denied", exc.reason, actor_user_id=identity.user.id, service_entry_id=service.id, context={"correlation_id": correlation_id, "client_category": "browser"})
            return safe_error("Service unavailable", "The protected service could not complete this request.", exc.status_code)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


async def handle_proxy_websocket(scope, receive, send, host: str, settings: Settings, session_factory) -> None:
    websocket = WebSocket(scope, receive=receive, send=send)
    correlation_id = websocket.headers.get("x-correlation-id", str(uuid.uuid4()))[:120]
    try:
        slug = service_slug_from_host(host, settings)
    except ValueError:
        slug = None
    with session_factory() as db:
        service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == slug)) if slug else None
        if service is None or not service.proxy_enabled or not service.websocket_enabled:
            if service is not None:
                record_event(db, "proxy_websocket_denied", "denied", "service_unavailable", service_entry_id=service.id, context={"correlation_id": correlation_id, "client_category": "browser"})
            await websocket.close(code=1008, reason="WebSocket access denied")
            return
        try:
            identity = authorize_proxy_cookie(db, websocket.cookies.get(settings.proxy_cookie_name), service, settings)
        except ProxyAuthorizationError as exc:
            record_event(db, "proxy_websocket_denied", "denied", exc.reason, service_entry_id=service.id, context={"correlation_id": correlation_id, "client_category": "browser"})
            await websocket.close(code=1008, reason="WebSocket access denied")
            return
        try:
            await relay_websocket(websocket, service, identity, settings)
        except ProxyWebSocketError as exc:
            record_event(db, "proxy_websocket_denied", "denied", exc.reason, actor_user_id=identity.user.id, service_entry_id=service.id, context={"correlation_id": correlation_id, "client_category": "browser"})
            try:
                await websocket.close(code=1011, reason="Protected service unavailable")
            except RuntimeError:
                pass
