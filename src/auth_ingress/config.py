from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

PRODUCT_NAME = "auth-ingress"
DISPLAY_NAME = "auth-ingress"
PREFERRED_COMMAND = "auth-ingress"
COMPATIBILITY_COMMAND = "auth-portal"
PREFERRED_CONFIG_PREFIX = "AUTH_INGRESS"
LEGACY_CONFIG_PREFIX = "AUTH_PORTAL"
REPOSITORY_URL = "https://github.com/zondatw/auth-ingress"


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
    password_reset_ttl_seconds: int = 1800
    reset_cookie: str = "auth_portal_reset"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_sender: str = ""
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    smtp_timeout_seconds: float = 5.0
    user_search_page_size: int = 50
    management_rate_limit_attempts: int = 60
    management_rate_limit_window_seconds: int = 60
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


def env_value(name: str, default: str) -> str:
    preferred = f"{PREFERRED_CONFIG_PREFIX}_{name}"
    legacy = f"{LEGACY_CONFIG_PREFIX}_{name}"
    value = os.getenv(preferred)
    if value is not None:
        return value
    return os.getenv(legacy, default)


@lru_cache
def get_settings() -> Settings:
    defaults = Settings()
    return Settings(
        database_url=env_value("DATABASE_URL", defaults.database_url),
        secret_key=env_value("SECRET_KEY", defaults.secret_key),
        session_cookie=env_value("SESSION_COOKIE", defaults.session_cookie),
        session_ttl_seconds=int(env_value("SESSION_TTL", str(defaults.session_ttl_seconds))),
        secure_cookies=env_value("SECURE_COOKIES", "false").lower() == "true",
        rate_limit_attempts=int(env_value("RATE_LIMIT_ATTEMPTS", str(defaults.rate_limit_attempts))),
        rate_limit_window_seconds=int(env_value("RATE_LIMIT_WINDOW", str(defaults.rate_limit_window_seconds))),
        audit_retention_days=max(90, int(env_value("AUDIT_RETENTION_DAYS", str(defaults.audit_retention_days)))),
        password_reset_ttl_seconds=max(300, int(env_value("PASSWORD_RESET_TTL", str(defaults.password_reset_ttl_seconds)))),
        reset_cookie=env_value("RESET_COOKIE", defaults.reset_cookie),
        smtp_host=env_value("SMTP_HOST", defaults.smtp_host),
        smtp_port=int(env_value("SMTP_PORT", str(defaults.smtp_port))),
        smtp_sender=env_value("SMTP_SENDER", defaults.smtp_sender),
        smtp_username=env_value("SMTP_USERNAME", defaults.smtp_username),
        smtp_password=env_value("SMTP_PASSWORD", defaults.smtp_password),
        smtp_starttls=env_value("SMTP_STARTTLS", "true").lower() == "true",
        smtp_timeout_seconds=max(1.0, float(env_value("SMTP_TIMEOUT", str(defaults.smtp_timeout_seconds)))),
        user_search_page_size=min(100, max(10, int(env_value("USER_PAGE_SIZE", str(defaults.user_search_page_size))))),
        management_rate_limit_attempts=max(5, int(env_value("MANAGEMENT_RATE_LIMIT_ATTEMPTS", str(defaults.management_rate_limit_attempts)))),
        management_rate_limit_window_seconds=max(10, int(env_value("MANAGEMENT_RATE_LIMIT_WINDOW", str(defaults.management_rate_limit_window_seconds)))),
        downstream_timeout_seconds=float(env_value("DOWNSTREAM_TIMEOUT", str(defaults.downstream_timeout_seconds))),
        portal_host=env_value("HOST", defaults.portal_host),
        proxy_base_domain=env_value("PROXY_BASE_DOMAIN", defaults.proxy_base_domain),
        proxy_scheme=env_value("PROXY_SCHEME", defaults.proxy_scheme),
        proxy_cookie_name=env_value("PROXY_COOKIE", defaults.proxy_cookie_name),
        proxy_launch_ttl_seconds=max(10, int(env_value("PROXY_LAUNCH_TTL", str(defaults.proxy_launch_ttl_seconds)))),
        proxy_max_request_bytes=max(1, int(env_value("PROXY_MAX_REQUEST_BYTES", str(defaults.proxy_max_request_bytes)))),
        proxy_max_response_bytes=max(1, int(env_value("PROXY_MAX_RESPONSE_BYTES", str(defaults.proxy_max_response_bytes)))),
        proxy_websocket_lifetime_seconds=max(1, int(env_value("PROXY_WEBSOCKET_LIFETIME", str(defaults.proxy_websocket_lifetime_seconds)))),
        trusted_downstream_networks=tuple(
            value.strip()
            for value in env_value("TRUSTED_DOWNSTREAM_NETWORKS", ",".join(defaults.trusted_downstream_networks)).split(",")
            if value.strip()
        ),
    )
