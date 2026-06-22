from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from urllib.parse import urlsplit

from fastapi import WebSocket
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

from auth_entry_portal.config import Settings
from auth_entry_portal.models import ServiceEntry
from auth_entry_portal.security.proxy_destination import UnsafeDestination, pin_destination, resolve_destination, websocket_destination
from auth_entry_portal.security.proxy_host import service_origin
from auth_entry_portal.services.proxy_authorization_service import ProxyIdentity
from auth_entry_portal.services.proxy_header_policy import filter_cookie_header
from auth_entry_portal.services.session_service import as_utc


class ProxyWebSocketError(RuntimeError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


_active_connections: set = set()


async def close_websockets() -> None:
    connections = list(_active_connections)
    if connections:
        await asyncio.gather(
            *(connection.close(code=1001, reason="portal shutdown") for connection in connections),
            return_exceptions=True,
        )
    _active_connections.clear()


async def _browser_to_upstream(browser: WebSocket, upstream) -> None:
    while True:
        message = await browser.receive()
        if message["type"] == "websocket.disconnect":
            return
        if message.get("text") is not None:
            await upstream.send(message["text"])
        elif message.get("bytes") is not None:
            await upstream.send(message["bytes"])


async def _upstream_to_browser(upstream, browser: WebSocket) -> None:
    async for message in upstream:
        if isinstance(message, str):
            await browser.send_text(message)
        else:
            await browser.send_bytes(message)


async def relay_websocket(
    browser: WebSocket,
    service: ServiceEntry,
    identity: ProxyIdentity,
    settings: Settings,
) -> None:
    try:
        configured_host, _, address = resolve_destination(service.destination, settings)
        target = websocket_destination(pin_destination(service.destination, address), browser.url.path, browser.scope.get("query_string", b""))
    except (UnsafeDestination, UnicodeError) as exc:
        raise ProxyWebSocketError("unsafe_destination") from exc
    raw_cookie = browser.headers.get("cookie", "")
    app_cookie = filter_cookie_header(raw_cookie, settings)
    headers = [("Cookie", app_cookie)] if app_cookie else []
    offered = list(browser.scope.get("subprotocols", []))
    now = datetime.now(timezone.utc)
    remaining = max(1, int((as_utc(identity.session.expires_at) - now).total_seconds()))
    lifetime = min(remaining, settings.proxy_websocket_lifetime_seconds)
    try:
        async with connect(
            target,
            origin=service_origin(service.slug, settings),
            subprotocols=offered or None,
            additional_headers=headers,
            open_timeout=settings.downstream_timeout_seconds,
            close_timeout=min(settings.downstream_timeout_seconds, 10),
            max_size=None,
            proxy=None,
            server_hostname=configured_host if target.startswith("wss://") else None,
        ) as upstream:
            _active_connections.add(upstream)
            await browser.accept(subprotocol=upstream.subprotocol)
            browser_task = asyncio.create_task(_browser_to_upstream(browser, upstream))
            upstream_task = asyncio.create_task(_upstream_to_browser(upstream, browser))
            try:
                async with asyncio.timeout(lifetime):
                    done, pending = await asyncio.wait(
                        {browser_task, upstream_task}, return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in done:
                        exception = task.exception()
                        if exception and not isinstance(exception, ConnectionClosed):
                            raise exception
                    for task in pending:
                        task.cancel()
                    await asyncio.gather(*pending, return_exceptions=True)
            except TimeoutError:
                await upstream.close(code=1000, reason="authorization lifetime ended")
                await browser.close(code=1000, reason="authorization lifetime ended")
            finally:
                for task in (browser_task, upstream_task):
                    if not task.done():
                        task.cancel()
                await asyncio.gather(browser_task, upstream_task, return_exceptions=True)
                _active_connections.discard(upstream)
    except ProxyWebSocketError:
        raise
    except Exception as exc:
        raise ProxyWebSocketError("upstream_websocket_unavailable") from exc
