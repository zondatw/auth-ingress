from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

OLD_NAME_TOKENS = (
    "auth-entry-portal",
    "auth-portal",
    "Auth Entry Portal",
    "Auth Portal",
    "auth_entry_portal",
    "auth_portal",
    "AUTH_PORTAL",
)

ALLOWED_CLASSIFICATIONS = {
    "compatibility alias",
    "historical reference",
    "security-stable identifier",
    "intentional exception",
}


@dataclass(frozen=True)
class RenameFinding:
    path: Path
    token: str
    classification: str


INTENTIONAL_OLD_NAME_REFERENCES: dict[str, str] = {
    "pyproject.toml": "compatibility alias",
    "README.md": "compatibility alias",
    "docs/user-management.md": "compatibility alias",
    "scripts/release/package_metadata.py": "compatibility alias",
    "src/auth_ingress/cli.py": "compatibility alias",
    "src/auth_ingress/config.py": "compatibility alias",
    "src/auth_ingress/main.py": "security-stable identifier",
    "src/auth_ingress/security/cookies.py": "security-stable identifier",
    "src/auth_ingress/security/csrf.py": "security-stable identifier",
    "src/auth_ingress/services/password_reset_service.py": "security-stable identifier",
    "src/auth_ingress/services/proxy_header_policy.py": "security-stable identifier",
    "src/auth_ingress/web/routes/proxy.py": "security-stable identifier",
    "tests/": "compatibility alias",
    "CHANGELOG.md": "historical reference",
    "SECURITY.md": "historical reference",
    "specs/003-publish-pypi/": "historical reference",
    "specs/004-manage-user-access/": "historical reference",
    "specs/005-rename-auth-ingress/": "historical reference",
}
