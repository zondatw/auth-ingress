from auth_ingress.services.cli_user_auth import authenticate_cli_actor


def test_compatibility_cli_uses_same_actor_authentication_service():
    assert authenticate_cli_actor.__module__ == "auth_ingress.services.cli_user_auth"

