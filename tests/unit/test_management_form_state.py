from auth_ingress.services.user_management_types import FieldError, ManagementFormState


def test_management_form_state_preserves_safe_values_and_excludes_sensitive_fields():
    state = ManagementFormState.from_submitted(
        "user_create",
        {
            "email": "new@example.test",
            "display_name": "New User",
            "temporary_password": "secret",
            "token": "opaque",
        },
    )

    assert state.value("email") == "new@example.test"
    assert state.value("display_name") == "New User"
    assert state.value("temporary_password") == ""
    assert state.value("token") == ""


def test_management_form_state_tracks_selected_values_and_field_errors():
    state = ManagementFormState.from_submitted(
        "service_create",
        {"proxy_enabled": "true"},
        selected={"group_ids": [1, "2"], "proxy_enabled": ["true"]},
        field_errors=[FieldError("group_ids", "One or more groups do not exist")],
        form_errors=["Fix the highlighted fields."],
    )

    assert state.is_selected("group_ids", 1)
    assert state.is_selected("group_ids", "2")
    assert state.checked("proxy_enabled") is True
    assert state.error_text("group_ids") == "One or more groups do not exist"
    assert state.form_errors == ["Fix the highlighted fields."]
