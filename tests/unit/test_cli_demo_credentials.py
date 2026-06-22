from __future__ import annotations

import pytest

from auth_entry_portal.cli import _demo_password


def test_demo_password_uses_account_specific_environment_variable(monkeypatch):
    monkeypatch.setenv("AUTH_PORTAL_DEMO_ADMIN_PASSWORD", "environment-secret")
    monkeypatch.setattr("auth_entry_portal.cli.getpass", lambda _prompt: pytest.fail("unexpected prompt"))

    assert _demo_password("admin") == "environment-secret"


def test_demo_password_prompts_without_environment_variable(monkeypatch):
    monkeypatch.delenv("AUTH_PORTAL_DEMO_MEMBER_PASSWORD", raising=False)
    monkeypatch.setattr("auth_entry_portal.cli.getpass", lambda prompt: "interactive-secret")

    assert _demo_password("member") == "interactive-secret"


def test_demo_password_rejects_short_values_without_disclosing_them(monkeypatch):
    monkeypatch.setenv("AUTH_PORTAL_DEMO_OUTSIDER_PASSWORD", "too-short")

    with pytest.raises(SystemExit) as error:
        _demo_password("outsider")

    message = str(error.value)
    assert "AUTH_PORTAL_DEMO_OUTSIDER_PASSWORD" in message
    assert "too-short" not in message
