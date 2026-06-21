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
    )
