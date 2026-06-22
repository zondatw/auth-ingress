from __future__ import annotations

from http.cookies import SimpleCookie
from urllib.parse import urlsplit, urlunsplit

from auth_portal.config import Settings

HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}
RESERVED_PREFIXES = ("auth_portal_", "__host-auth_portal", "__secure-auth_portal")


class UnsafeRedirect(ValueError):
    pass


def _connection_tokens(headers: list[tuple[bytes, bytes]]) -> set[str]:
    tokens: set[str] = set()
    for name, value in headers:
        if name.decode("latin-1").casefold() == "connection":
            tokens.update(item.strip().casefold() for item in value.decode("latin-1").split(","))
    return tokens


def filter_request_headers(
    raw_headers: list[tuple[bytes, bytes]],
    settings: Settings,
    upstream_authority: str,
    correlation_id: str,
) -> list[tuple[bytes, bytes]]:
    blocked = HOP_BY_HOP | _connection_tokens(raw_headers) | {"host", "authorization", "x-forwarded-host", "x-forwarded-proto", "x-forwarded-for"}
    result: list[tuple[bytes, bytes]] = []
    for raw_name, raw_value in raw_headers:
        name = raw_name.decode("latin-1").casefold()
        if name in blocked:
            continue
        if name == "cookie":
            value = filter_cookie_header(raw_value.decode("latin-1"), settings)
            if value:
                result.append((b"cookie", value.encode("latin-1")))
            continue
        result.append((raw_name, raw_value))
    result.extend(
        [
            (b"host", upstream_authority.encode("ascii")),
            (b"x-correlation-id", correlation_id[:120].encode("ascii", errors="ignore")),
            (b"x-forwarded-proto", settings.proxy_scheme.encode("ascii")),
        ]
    )
    return result


def filter_cookie_header(value: str, settings: Settings) -> str:
    cookie = SimpleCookie()
    try:
        cookie.load(value)
    except Exception:
        return ""
    blocked = {settings.session_cookie.casefold(), settings.proxy_cookie_name.casefold()}
    return "; ".join(f"{key}={morsel.value}" for key, morsel in cookie.items() if key.casefold() not in blocked and not key.casefold().startswith(RESERVED_PREFIXES))


def rewrite_set_cookie(value: str, settings: Settings) -> str | None:
    parts = [part.strip() for part in value.split(";") if part.strip()]
    if not parts or "=" not in parts[0]:
        return None
    name = parts[0].split("=", 1)[0].strip().casefold()
    if name in {settings.session_cookie.casefold(), settings.proxy_cookie_name.casefold()} or name.startswith(RESERVED_PREFIXES):
        return None
    safe = [parts[0]]
    for part in parts[1:]:
        attribute = part.split("=", 1)[0].strip().casefold()
        if attribute == "domain":
            continue
        safe.append(part)
    return "; ".join(safe)


def filter_response_headers(raw_headers: list[tuple[bytes, bytes]], settings: Settings) -> list[tuple[bytes, bytes]]:
    blocked = HOP_BY_HOP | _connection_tokens(raw_headers) | {"server", "proxy-status", "www-authenticate"}
    result: list[tuple[bytes, bytes]] = []
    for raw_name, raw_value in raw_headers:
        name = raw_name.decode("latin-1").casefold()
        if name in blocked:
            continue
        if name == "set-cookie":
            rewritten = rewrite_set_cookie(raw_value.decode("latin-1"), settings)
            if rewritten:
                result.append((b"set-cookie", rewritten.encode("latin-1")))
            continue
        result.append((raw_name, raw_value))
    return result


def rewrite_location(location: str, destination: str, public_origin: str) -> str:
    target = urlsplit(location)
    if not target.scheme and not target.netloc:
        return location
    upstream = urlsplit(destination)
    if target.username or target.password or target.scheme not in {"http", "https"}:
        raise UnsafeRedirect("unsafe redirect")
    target_port = target.port or (443 if target.scheme == "https" else 80)
    upstream_port = upstream.port or (443 if upstream.scheme == "https" else 80)
    if target.hostname != upstream.hostname or target_port != upstream_port:
        raise UnsafeRedirect("external redirect denied")
    public = urlsplit(public_origin)
    return urlunsplit((public.scheme, public.netloc, target.path, target.query, target.fragment))
