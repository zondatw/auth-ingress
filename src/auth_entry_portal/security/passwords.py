from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()
_dummy_hash = _hasher.hash("constant-time-dummy-password")


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError("password must contain at least 10 characters")
    return _hasher.hash(password)


def verify_password(password_hash: str | None, password: str) -> bool:
    candidate = password_hash or _dummy_hash
    try:
        valid = _hasher.verify(candidate, password)
    except (VerificationError, InvalidHashError):
        valid = False
    return bool(valid and password_hash)

