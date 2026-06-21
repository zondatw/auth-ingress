from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from auth_portal.config import Settings


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

