import inspect

from auth_ingress.services.cli_user_auth import authenticate_cli_actor


def test_cli_auth_has_no_password_argument_or_environment_path():
    source = inspect.getsource(authenticate_cli_actor).casefold()
    assert "getenv" not in source
    assert "password=" not in source


def test_cli_denial_is_generic(db):
    result = authenticate_cli_actor(db, "missing@example.test", "wrong")
    assert result is None
