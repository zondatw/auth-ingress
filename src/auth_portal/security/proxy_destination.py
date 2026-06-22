from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from urllib.parse import quote, urlsplit, urlunsplit

from auth_portal.config import Settings


class UnsafeDestination(ValueError):
    pass


Resolver = Callable[..., list[tuple]]


def trusted_networks(settings: Settings) -> tuple[ipaddress._BaseNetwork, ...]:
    try:
        return tuple(ipaddress.ip_network(value, strict=False) for value in settings.trusted_downstream_networks)
    except ValueError as exc:
        raise UnsafeDestination("invalid trusted network configuration") from exc


def resolve_destination(destination: str, settings: Settings, resolver: Resolver = socket.getaddrinfo) -> tuple[str, int, str]:
    parsed = urlsplit(destination)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise UnsafeDestination("invalid fixed destination")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        answers = resolver(parsed.hostname, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise UnsafeDestination("destination resolution failed") from exc
    if not answers:
        raise UnsafeDestination("destination resolution failed")
    networks = trusted_networks(settings)
    addresses = {answer[4][0] for answer in answers}
    try:
        parsed_addresses = [ipaddress.ip_address(value) for value in addresses]
    except ValueError as exc:
        raise UnsafeDestination("invalid destination address") from exc
    if any(not any(address in network for network in networks) for address in parsed_addresses):
        raise UnsafeDestination("destination address is not trusted")
    selected = sorted(parsed_addresses, key=lambda value: (value.version, str(value)))[0]
    return parsed.hostname, port, str(selected)


def pin_destination(destination: str, address: str) -> str:
    parsed = urlsplit(destination)
    ip = ipaddress.ip_address(address)
    host = f"[{ip}]" if ip.version == 6 else str(ip)
    port = parsed.port
    default = 443 if parsed.scheme == "https" else 80
    netloc = host if port in {None, default} else f"{host}:{port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))


def join_destination(destination: str, path: str, raw_query: bytes = b"") -> str:
    parsed = urlsplit(destination)
    decoded_segments = [segment for segment in path.replace("\\", "/").split("/") if segment]
    if any(segment in {".", ".."} for segment in decoded_segments):
        raise UnsafeDestination("unsafe path")
    base = parsed.path.rstrip("/")
    encoded_path = "/".join(quote(segment, safe="!$&'()*+,;=:@-._~%") for segment in decoded_segments)
    joined = f"{base}/{encoded_path}" if encoded_path else (base or "/")
    query = raw_query.decode("ascii", errors="strict") if raw_query else ""
    return urlunsplit((parsed.scheme, parsed.netloc, joined, query, ""))


def websocket_destination(destination: str, path: str, raw_query: bytes = b"") -> str:
    target = urlsplit(join_destination(destination, path, raw_query))
    scheme = "wss" if target.scheme == "https" else "ws"
    return urlunsplit((scheme, target.netloc, target.path, target.query, ""))
