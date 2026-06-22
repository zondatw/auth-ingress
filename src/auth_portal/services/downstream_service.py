from __future__ import annotations

import asyncio
import httpx


class DownstreamUnavailable(Exception):
    pass


_clients: dict[tuple[float, int], httpx.AsyncClient] = {}


def pooled_client(timeout_seconds: float) -> httpx.AsyncClient:
    key = (timeout_seconds, id(asyncio.get_running_loop()))
    client = _clients.get(key)
    if client is None or client.is_closed:
        client = httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds), follow_redirects=False)
        _clients[key] = client
    return client


async def close_clients() -> None:
    for client in _clients.values():
        if not client.is_closed:
            await client.aclose()
    _clients.clear()


async def fetch_downstream(destination: str, timeout_seconds: float) -> tuple[bytes, str]:
    if destination.startswith("mock://"):
        name = destination.removeprefix("mock://") or "service"
        return f"<main><h1>{name.title()}</h1><p>Protected service reached.</p></main>".encode(), "text/html; charset=utf-8"
    try:
        response = await pooled_client(timeout_seconds).get(destination)
        response.raise_for_status()
    except (httpx.HTTPError, ValueError) as exc:
        raise DownstreamUnavailable from exc
    return response.content, response.headers.get("content-type", "application/octet-stream")
