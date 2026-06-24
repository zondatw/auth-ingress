from auth_ingress.config import get_settings


def test_new_prefix_overrides_old_prefix_for_same_setting(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("AUTH_PORTAL_DATABASE_URL", "sqlite:///old.db")
    monkeypatch.setenv("AUTH_INGRESS_DATABASE_URL", "sqlite:///new.db")
    assert get_settings().database_url == "sqlite:///new.db"
    get_settings.cache_clear()


def test_old_prefix_fallback_remains_available(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.delenv("AUTH_INGRESS_DATABASE_URL", raising=False)
    monkeypatch.setenv("AUTH_PORTAL_DATABASE_URL", "sqlite:///old.db")
    assert get_settings().database_url == "sqlite:///old.db"
    get_settings.cache_clear()

