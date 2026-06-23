from auth_entry_portal.config import get_settings


def test_auth_ingress_environment_takes_precedence(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("AUTH_PORTAL_HOST", "old.example.test")
    monkeypatch.setenv("AUTH_INGRESS_HOST", "new.example.test")
    assert get_settings().portal_host == "new.example.test"
    get_settings.cache_clear()


def test_auth_portal_environment_remains_compatible(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.delenv("AUTH_INGRESS_HOST", raising=False)
    monkeypatch.setenv("AUTH_PORTAL_HOST", "legacy.example.test")
    assert get_settings().portal_host == "legacy.example.test"
    get_settings.cache_clear()

