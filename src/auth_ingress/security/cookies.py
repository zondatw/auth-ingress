from datetime import datetime, timezone

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from auth_ingress.config import Settings


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt="auth-portal-session-v1")


def encode_session_id(session_id: str, settings: Settings) -> str:
    return _serializer(settings).dumps({"sid": session_id})


def decode_session_id(value: str | None, settings: Settings) -> str | None:
    if not value:
        return None
    try:
        payload = _serializer(settings).loads(value, max_age=settings.session_ttl_seconds)
    except (BadSignature, SignatureExpired):
        return None
    session_id = payload.get("sid")
    return session_id if isinstance(session_id, str) else None


def cookie_options(settings: Settings) -> dict:
    return {
        "httponly": True,
        "secure": settings.secure_cookies,
        "samesite": "lax",
        "max_age": settings.session_ttl_seconds,
        "path": "/",
    }


def _proxy_serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt="auth-portal-service-proxy-v1")


def encode_proxy_credential(session_id: str, service_id: int, expires_at: datetime, settings: Settings) -> str:
    expiry = int(expires_at.replace(tzinfo=expires_at.tzinfo or timezone.utc).timestamp())
    return _proxy_serializer(settings).dumps({"sid": session_id, "service": service_id, "exp": expiry, "v": 1})


def decode_proxy_credential(value: str | None, settings: Settings) -> tuple[str, int] | None:
    if not value:
        return None
    try:
        payload = _proxy_serializer(settings).loads(value, max_age=settings.session_ttl_seconds)
        if payload.get("v") != 1 or int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            return None
        return str(payload["sid"]), int(payload["service"])
    except (BadSignature, SignatureExpired, KeyError, TypeError, ValueError):
        return None


def proxy_cookie_options(settings: Settings, max_age: int) -> dict:
    return {
        "httponly": True,
        "secure": settings.secure_cookies,
        "samesite": "lax",
        "max_age": max(0, max_age),
        "path": "/",
    }
