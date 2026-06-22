from __future__ import annotations

from scripts.release.verify_index import safe_summary
from tests.release_helpers import ROOT


def test_summary_allows_only_release_identity_and_safe_outcome():
    source = {
        "version": "0.1.0",
        "revision": "a" * 40,
        "outcome": "completed",
        "reason": "hashes-match",
        "hashes": {"file.whl": "b" * 64},
        "oidc_token": "publisher-secret",
        "session": "browser-secret",
        "database": "private-content",
        "email": "person@example.test",
    }
    summary = safe_summary(source)
    assert set(summary) == {"version", "revision", "outcome", "reason", "hashes"}
    rendered = repr(summary).lower()
    for value in ("publisher-secret", "browser-secret", "private-content", "person@example.test"):
        assert value not in rendered


def test_release_files_contain_no_static_credentials_or_demo_secrets():
    paths = [
        ROOT / ".github" / "workflows" / "release.yml",
        ROOT / ".github" / "RELEASE_SETUP.md",
        ROOT / "docs" / "releasing.md",
        ROOT / "docs" / "release-recovery.md",
    ]
    assert all(path.is_file() for path in paths)
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    forbidden = (
        "demo-admin-password",
        "demo-member-password",
        "demo-outsider-password",
        "pypi_api_token",
        "twine_password",
        "secrets.",
    )
    assert not any(value in text for value in forbidden)
