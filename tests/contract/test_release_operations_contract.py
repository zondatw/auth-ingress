from __future__ import annotations

from tests.release_helpers import ROOT


def read_runbooks() -> str:
    paths = (ROOT / "docs" / "releasing.md", ROOT / "docs" / "release-recovery.md")
    assert all(path.is_file() for path in paths)
    return "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()


def test_release_runbooks_preserve_immutable_versions_and_evidence():
    text = read_runbooks()
    normalized = " ".join(text.split())
    for phrase in (
        "never overwrite",
        "new version",
        "yank",
        "sha-256",
        "90 days",
        "release notes",
    ):
        assert phrase in text
    assert "never overwrite or delete and republish" in normalized
    assert "you can delete and republish" not in normalized
    assert "skip-existing" not in text


def test_recovery_runbook_covers_revocation_notification_and_separation():
    text = read_runbooks()
    for phrase in (
        "trusted publisher",
        "revoke",
        "cancel",
        "notify",
        "application credentials",
        "investigation",
    ):
        assert phrase in text
