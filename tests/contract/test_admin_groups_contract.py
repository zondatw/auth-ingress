from auth_ingress.models import Group
from tests.conftest import sign_in


def test_group_list_and_detail_contract(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    listing = client.get("/admin/groups")
    assert listing.status_code == 200
    assert "Groups" in listing.text
    assert "staff" in listing.text
    assert "admins" in listing.text
    assert "Users" in listing.text
    assert "Services" in listing.text

    detail = client.get("/admin/groups?usage=used")
    assert detail.status_code == 200
    assert "staff" in detail.text
    assert "No groups found" not in detail.text


def test_group_detail_dependency_contract(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    staff = db.query(Group).filter_by(name="staff").one()

    response = client.get(f"/admin/groups/{staff.id}")

    assert response.status_code == 200
    assert "Dependencies" in response.text
    assert "member@example.test" in response.text
    assert "Demo Service" in response.text
    assert "Access impact" in response.text


def test_create_group_validation_preserves_values_and_field_errors(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    response = client.post("/admin/groups", data={"csrf": csrf, "name": " staff ", "description": "Duplicate"})

    assert response.status_code == 400
    assert "Group name is already in use" in response.text
    assert 'name="name" value=" staff "' in response.text
    assert 'name="description" value="Duplicate"' in response.text
    assert "field-error" in response.text


def test_create_group_success_redirects_to_detail(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    response = client.post("/admin/groups", data={"csrf": csrf, "name": "ops", "description": "Operations"}, follow_redirects=False)

    assert response.status_code == 303
    detail = client.get(response.headers["location"])
    assert "ops" in detail.text
    assert "Operations" in detail.text


def test_edit_group_preview_confirm_and_stale_contract(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    group = db.query(Group).filter_by(name="staff").one()

    preview = client.post(
        f"/admin/groups/{group.id}/profile",
        data={"csrf": csrf, "expected_revision": group.revision, "name": "staff team", "description": "Staff team"},
    )
    assert preview.status_code == 200
    assert "Preview group update" in preview.text
    assert "Confirm group changes" in preview.text

    stale = client.post(
        f"/admin/groups/{group.id}/profile",
        data={"csrf": csrf, "expected_revision": group.revision + 100, "name": "staff stale", "description": ""},
    )
    assert stale.status_code == 409
    assert "Group changed; refresh and try again" in stale.text


def test_lifecycle_contract_dependency_block_and_unused_remove(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    staff = db.query(Group).filter_by(name="staff").one()
    unused = Group(name="temp", description="")
    db.add(unused)
    db.commit()

    blocked = client.post(
        f"/admin/groups/{staff.id}/lifecycle",
        data={"csrf": csrf, "expected_revision": staff.revision, "action": "remove"},
    )
    assert blocked.status_code == 409
    assert "Group still has users or services" in blocked.text

    preview = client.post(
        f"/admin/groups/{unused.id}/lifecycle",
        data={"csrf": csrf, "expected_revision": unused.revision, "action": "remove"},
    )
    assert preview.status_code == 200
    assert "Preview group remove" in preview.text
    assert "Confirm remove" in preview.text
