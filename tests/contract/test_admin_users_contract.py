from tests.conftest import sign_in


def test_admin_user_list_and_detail_contract(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    listing = client.get("/admin/users")
    assert listing.status_code == 200
    assert "member@example.test" in listing.text
    detail = client.get(f"/admin/users/{db.query(__import__('auth_ingress.models', fromlist=['User']).User).filter_by(email='member@example.test').one().id}")
    assert detail.status_code == 200
    assert "Demo Service" in detail.text
    assert "staff" in detail.text


def test_membership_preview_does_not_write(client, csrf, db_factory, db):
    sign_in(client, csrf, email="admin@example.test")
    user = db.query(__import__("auth_ingress.models", fromlist=["User"]).User).filter_by(email="outsider@example.test").one()
    group = db.query(__import__("auth_ingress.models", fromlist=["Group"]).Group).filter_by(name="staff").one()
    response = client.post(f"/admin/users/{user.id}/memberships", data={"csrf": csrf, "expected_revision": user.revision, "group_ids": str(group.id)})
    assert response.status_code == 200
    assert "Preview changes" in response.text
    with db_factory() as check:
        assert check.query(__import__("auth_ingress.models", fromlist=["GroupMembership"]).GroupMembership).filter_by(user_id=user.id).count() == 0


def test_invalid_user_create_preserves_safe_values_and_selected_groups(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    group = db.query(__import__("auth_ingress.models", fromlist=["Group"]).Group).filter_by(name="staff").one()

    response = client.post(
        "/admin/users/preview",
        data={
            "csrf": csrf,
            "email": "not-an-email",
            "display_name": "New User",
            "status": "disabled",
            "is_admin": "true",
            "group_ids": str(group.id),
        },
    )

    assert response.status_code == 400
    assert 'name="email" value="not-an-email"' in response.text
    assert 'name="display_name" value="New User"' in response.text
    assert '<option value="disabled" selected>disabled</option>' in response.text
    assert 'name="is_admin" value="true" checked' in response.text
    assert f'name="group_ids" value="{group.id}" checked' in response.text
    assert "Valid email is required" in response.text
    assert "Temporary password" not in response.text


def test_invalid_membership_preserves_selected_groups(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    user = db.query(__import__("auth_ingress.models", fromlist=["User"]).User).filter_by(email="outsider@example.test").one()
    group = db.query(__import__("auth_ingress.models", fromlist=["Group"]).Group).filter_by(name="staff").one()

    response = client.post(
        f"/admin/users/{user.id}/memberships",
        data={"csrf": csrf, "expected_revision": user.revision, "group_ids": [str(group.id), "999999"]},
    )

    assert response.status_code == 400
    assert f'name="group_ids" value="{group.id}" checked' in response.text
    assert "One or more groups do not exist" in response.text
