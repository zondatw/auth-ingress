from auth_ingress.models import AccessRule, Group, GroupMembership, ServiceEntry, User
from auth_ingress.services.access_service import may_enter
from tests.conftest import sign_in


def test_group_search_filters_dependency_counts_and_empty_state(client, csrf):
    sign_in(client, csrf, email="admin@example.test")

    filtered = client.get("/admin/groups?q=staff&usage=used")
    assert filtered.status_code == 200
    assert "staff" in filtered.text
    assert "admins" not in filtered.text

    empty = client.get("/admin/groups?q=no-such-group")
    assert empty.status_code == 200
    assert "No groups found" in empty.text


def test_group_create_edit_duplicate_and_stale_recovery(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")

    created = client.post("/admin/groups", data={"csrf": csrf, "name": "platform", "description": "Platform"}, follow_redirects=False)
    assert created.status_code == 303
    group_id = int(created.headers["location"].rstrip("/").split("/")[-1])
    group = db.get(Group, group_id)

    duplicate = client.post("/admin/groups", data={"csrf": csrf, "name": " Platform ", "description": "again"})
    assert duplicate.status_code == 400
    assert "again" in duplicate.text

    preview = client.post(
        f"/admin/groups/{group.id}/profile",
        data={"csrf": csrf, "expected_revision": group.revision, "name": "platform ops", "description": "Ops"},
    )
    assert "Confirm group changes" in preview.text
    confirm = client.post(
        f"/admin/groups/{group.id}/profile",
        data={"csrf": csrf, "expected_revision": group.revision, "name": "platform ops", "description": "Ops", "confirm": "true"},
    )
    assert "Group updated" in confirm.text


def test_deactivated_group_stops_effective_access_and_reactivation_restores(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    staff = db.query(Group).filter_by(name="staff").one()
    member = db.query(User).filter_by(email="member@example.test").one()
    service = db.query(ServiceEntry).filter_by(slug="demo").one()
    assert may_enter(db, member, service) is True

    preview = client.post(
        f"/admin/groups/{staff.id}/lifecycle",
        data={"csrf": csrf, "expected_revision": staff.revision, "action": "deactivate"},
    )
    assert "Preview group deactivate" in preview.text
    confirm = client.post(
        f"/admin/groups/{staff.id}/lifecycle",
        data={"csrf": csrf, "expected_revision": staff.revision, "action": "deactivate", "confirm": "true"},
    )
    assert "Group deactivated" in confirm.text
    db.refresh(staff)
    assert may_enter(db, member, service) is False

    reactivate = client.post(
        f"/admin/groups/{staff.id}/lifecycle",
        data={"csrf": csrf, "expected_revision": staff.revision, "action": "reactivate", "confirm": "true"},
    )
    assert "Group reactivated" in reactivate.text
    assert may_enter(db, member, service) is True


def test_removal_blocked_for_used_group_and_succeeds_for_unused(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    staff = db.query(Group).filter_by(name="staff").one()
    unused = Group(name="cleanup", description="")
    db.add(unused)
    db.commit()
    unused_id = unused.id

    blocked = client.post(
        f"/admin/groups/{staff.id}/lifecycle",
        data={"csrf": csrf, "expected_revision": staff.revision, "action": "remove", "confirm": "true"},
    )
    assert blocked.status_code == 409
    assert db.get(Group, staff.id) is not None

    removed = client.post(
        f"/admin/groups/{unused_id}/lifecycle",
        data={"csrf": csrf, "expected_revision": unused.revision, "action": "remove", "confirm": "true"},
    )
    assert removed.status_code == 200
    assert "Group removed" in removed.text
    db.expire_all()
    assert db.get(Group, unused_id) is None
