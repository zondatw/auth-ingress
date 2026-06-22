from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str = "sqlite:///./auth_portal.db"
    secret_key: str = "development-only-change-me"
    session_cookie: str = "auth_portal_session"
    session_ttl_seconds: int = 3600
    secure_cookies: bool = False
    rate_limit_attempts: int = 5
    rate_limit_window_seconds: int = 300
    audit_retention_days: int = 90
    downstream_timeout_seconds: float = 5.0
    portal_host: str = "127.0.0.1:8000"
    proxy_base_domain: str = "localhost:8000"
    proxy_scheme: str = "http"
    proxy_cookie_name: str = "auth_portal_service"
    proxy_launch_ttl_seconds: int = 60
    proxy_max_request_bytes: int = 50 * 1024 * 1024
    proxy_max_response_bytes: int = 100 * 1024 * 1024
    proxy_websocket_lifetime_seconds: int = 3600
    trusted_downstream_networks: tuple[str, ...] = (
        "127.0.0.0/8",
        "::1/128",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
    )


@lru_cache
def get_settings() -> Settings:
    defaults = Settings()
    return Settings(
        database_url=os.getenv("AUTH_PORTAL_DATABASE_URL", defaults.database_url),
        secret_key=os.getenv("AUTH_PORTAL_SECRET_KEY", defaults.secret_key),
        session_cookie=os.getenv("AUTH_PORTAL_SESSION_COOKIE", defaults.session_cookie),
        session_ttl_seconds=int(os.getenv("AUTH_PORTAL_SESSION_TTL", defaults.session_ttl_seconds)),
        secure_cookies=os.getenv("AUTH_PORTAL_SECURE_COOKIES", "false").lower() == "true",
        rate_limit_attempts=int(os.getenv("AUTH_PORTAL_RATE_LIMIT_ATTEMPTS", defaults.rate_limit_attempts)),
        rate_limit_window_seconds=int(os.getenv("AUTH_PORTAL_RATE_LIMIT_WINDOW", defaults.rate_limit_window_seconds)),
        audit_retention_days=max(90, int(os.getenv("AUTH_PORTAL_AUDIT_RETENTION_DAYS", defaults.audit_retention_days))),
        downstream_timeout_seconds=float(os.getenv("AUTH_PORTAL_DOWNSTREAM_TIMEOUT", defaults.downstream_timeout_seconds)),
        portal_host=os.getenv("AUTH_PORTAL_HOST", defaults.portal_host),
        proxy_base_domain=os.getenv("AUTH_PORTAL_PROXY_BASE_DOMAIN", defaults.proxy_base_domain),
        proxy_scheme=os.getenv("AUTH_PORTAL_PROXY_SCHEME", defaults.proxy_scheme),
        proxy_cookie_name=os.getenv("AUTH_PORTAL_PROXY_COOKIE", defaults.proxy_cookie_name),
        proxy_launch_ttl_seconds=max(10, int(os.getenv("AUTH_PORTAL_PROXY_LAUNCH_TTL", defaults.proxy_launch_ttl_seconds))),
        proxy_max_request_bytes=max(1, int(os.getenv("AUTH_PORTAL_PROXY_MAX_REQUEST_BYTES", defaults.proxy_max_request_bytes))),
        proxy_max_response_bytes=max(1, int(os.getenv("AUTH_PORTAL_PROXY_MAX_RESPONSE_BYTES", defaults.proxy_max_response_bytes))),
        proxy_websocket_lifetime_seconds=max(1, int(os.getenv("AUTH_PORTAL_PROXY_WEBSOCKET_LIFETIME", defaults.proxy_websocket_lifetime_seconds))),
        trusted_downstream_networks=tuple(
            value.strip()
            for value in os.getenv("AUTH_PORTAL_TRUSTED_DOWNSTREAM_NETWORKS", ",".join(defaults.trusted_downstream_networks)).split(",")
            if value.strip()
        ),
    )
