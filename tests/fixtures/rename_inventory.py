from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

OLD_NAME_TOKENS = (
    "auth-entry-portal",
    "auth-portal",
    "Auth Entry Portal",
    "Auth Portal",
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
    "src/auth_entry_portal/cli.py": "compatibility alias",
    "src/auth_entry_portal/config.py": "compatibility alias",
    "src/auth_entry_portal/main.py": "security-stable identifier",
    "src/auth_entry_portal/security/cookies.py": "security-stable identifier",
    "src/auth_entry_portal/security/csrf.py": "security-stable identifier",
    "src/auth_entry_portal/services/password_reset_service.py": "security-stable identifier",
    "src/auth_entry_portal/services/proxy_header_policy.py": "security-stable identifier",
    "src/auth_entry_portal/web/routes/proxy.py": "security-stable identifier",
    "tests/": "compatibility alias",
    "specs/003-publish-pypi/": "historical reference",
    "specs/004-manage-user-access/": "historical reference",
    "specs/005-rename-auth-ingress/": "historical reference",
}
