from __future__ import annotations

from collections.abc import AsyncIterator
from urllib.parse import urlsplit

import httpx
from fastapi import Request
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from auth_portal.config import Settings
from auth_portal.models import ServiceEntry
from auth_portal.security.proxy_destination import UnsafeDestination, join_destination, pin_destination, resolve_destination
from auth_portal.security.proxy_host import service_origin
from auth_portal.services.downstream_service import pooled_client
from auth_portal.services.proxy_header_policy import (
    UnsafeRedirect,
    filter_request_headers,
    filter_response_headers,
    rewrite_location,
)


class ProxyHTTPError(RuntimeError):
    def __init__(self, reason: str, status_code: int):
        super().__init__(reason)
        self.reason = reason
        self.status_code = status_code


async def limited_request_stream(request: Request, maximum: int) -> AsyncIterator[bytes]:
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > maximum:
            raise ProxyHTTPError("request_too_large", 413)
        yield chunk


async def limited_response_stream(response: httpx.Response, maximum: int) -> AsyncIterator[bytes]:
    size = 0
    async for chunk in response.aiter_raw():
        size += len(chunk)
        if size > maximum:
            raise ProxyHTTPError("response_too_large", 502)
        yield chunk


async def forward_http(request: Request, service: ServiceEntry, settings: Settings) -> StreamingResponse:
    try:
        configured_host, _, address = resolve_destination(service.destination, settings)
        target = join_destination(pin_destination(service.destination, address), request.url.path, request.scope.get("query_string", b""))
    except (UnsafeDestination, UnicodeError) as exc:
        raise ProxyHTTPError("unsafe_destination", 502) from exc
    parsed = urlsplit(service.destination)
    authority = parsed.netloc
    headers = filter_request_headers(
        list(request.headers.raw),
        settings,
        authority,
        getattr(request.state, "correlation_id", ""),
    )
    client = pooled_client(settings.downstream_timeout_seconds)
    try:
        upstream_request = httpx.Request(
            request.method,
            target,
            headers=headers,
            content=limited_request_stream(request, settings.proxy_max_request_bytes),
        )
        upstream_request.extensions["sni_hostname"] = configured_host.encode("idna")
        upstream = await client.send(upstream_request, stream=True)
    except httpx.ConnectTimeout as exc:
        raise ProxyHTTPError("upstream_connect_timeout", 503) from exc
    except httpx.ReadTimeout as exc:
        raise ProxyHTTPError("upstream_read_timeout", 504) from exc
    except (httpx.HTTPError, ProxyHTTPError) as exc:
        if isinstance(exc, ProxyHTTPError):
            raise
        raise ProxyHTTPError("upstream_unavailable", 503) from exc

    content_length = upstream.headers.get("content-length")
    if content_length and int(content_length) > settings.proxy_max_response_bytes:
        await upstream.aclose()
        raise ProxyHTTPError("response_too_large", 502)

    raw_headers = filter_response_headers(list(upstream.headers.raw), settings)
    location_indexes = [index for index, (name, _) in enumerate(raw_headers) if name.decode("latin-1").casefold() == "location"]
    try:
        for index in location_indexes:
            name, value = raw_headers[index]
            rewritten = rewrite_location(value.decode("latin-1"), service.destination, service_origin(service.slug, settings))
            raw_headers[index] = (name, rewritten.encode("latin-1"))
    except UnsafeRedirect as exc:
        await upstream.aclose()
        raise ProxyHTTPError("unsafe_redirect", 502) from exc

    body = [] if request.method == "HEAD" else limited_response_stream(upstream, settings.proxy_max_response_bytes)
    response = StreamingResponse(body, status_code=upstream.status_code, background=BackgroundTask(upstream.aclose))
    response.raw_headers = raw_headers
    return response
