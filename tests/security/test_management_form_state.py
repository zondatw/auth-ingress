from auth_ingress.services.user_management_types import ManagementFormState
from tests.conftest import sign_in


def test_management_form_state_never_preserves_sensitive_fields():
    state = ManagementFormState.from_submitted(
        "sensitive",
        {
            "email": "new@example.test",
            "password": "secret-password",
            "temporary_password": "one-time-secret",
            "token": "opaque-token",
            "recovery_token": "recover-me",
        },
    )

    assert state.value("email") == "new@example.test"
    assert state.value("password") == ""
    assert state.value("temporary_password") == ""
    assert state.value("token") == ""
    assert state.value("recovery_token") == ""


def test_failed_user_create_does_not_echo_temporary_password_or_secret_words(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    response = client.post(
        "/admin/users/preview",
        data={
            "csrf": csrf,
            "email": "bad-email",
            "display_name": "Secret Candidate",
            "status": "active",
            "temporary_password": "must-not-return",
            "token": "token-must-not-return",
        },
    )

    assert response.status_code == 400
    assert "must-not-return" not in response.text
    assert "token-must-not-return" not in response.text
    assert "Temporary password" not in response.text
