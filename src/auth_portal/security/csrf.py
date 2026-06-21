from itsdangerous import BadSignature, URLSafeSerializer

from auth_portal.config import Settings


def csrf_token(settings: Settings) -> str:
    return URLSafeSerializer(settings.secret_key, salt="auth-portal-csrf-v1").dumps("form")


def valid_csrf(token: str, settings: Settings) -> bool:
    try:
        return URLSafeSerializer(settings.secret_key, salt="auth-portal-csrf-v1").loads(token) == "form"
    except BadSignature:
        return False

