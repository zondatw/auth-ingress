import inspect

import pytest

from auth_entry_portal.services.bootstrap_service import BootstrapError, bootstrap_admin


def test_bootstrap_rejects_invalid_input_without_partial_user(db_factory):
    with db_factory() as db:
        with pytest.raises((BootstrapError, ValueError)):
            bootstrap_admin(db, "not-an-email", "Admin", "short")
        assert db.query(__import__("auth_entry_portal.models", fromlist=["User"]).User).count() == 0


def test_bootstrap_service_has_no_logging_or_environment_secret_path():
    source = inspect.getsource(bootstrap_admin).casefold()
    assert "getenv" not in source
    assert "password=" not in source
    assert "logger" not in source
