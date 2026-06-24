from auth_ingress.models import PortalSession, User
from auth_ingress.services.authentication_service import authenticate
from auth_ingress.services.user_admin_service import create_user, set_user_status, update_user
from auth_ingress.services.user_management_types import OutcomeCode
from tests.conftest import sign_in
from tests.fixtures.recovery_delivery import CapturingRecoveryDelivery


def test_create_update_disable_and_reactivate(db, settings):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    delivery = CapturingRecoveryDelivery()
    preview = create_user(db, actor, "new@example.test", "New User", "active", False, set(), apply=False, settings=settings, delivery=delivery, base_url="https://portal.test")
    assert preview.outcome == OutcomeCode.SUCCESS and db.query(User).filter_by(email="new@example.test").first() is None
    created = create_user(db, actor, "new@example.test", "New User", "active", False, set(), apply=True, settings=settings, delivery=delivery, base_url="https://portal.test")
    target = db.get(User, created.target_user_id)
    assert target.credential_status == "temporary"
    assert created.temporary_password
    assert not delivery.messages
    assert authenticate(db, "new@example.test", created.temporary_password) == target
    changed = update_user(db, actor, target.id, target.revision, display_name="Renamed", apply=True)
    assert changed.outcome == OutcomeCode.SUCCESS
    session = PortalSession(id="lifecycle-session", user_id=target.id, expires_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc) + __import__("datetime").timedelta(hours=1))
    db.add(session); db.commit()
    disabled = set_user_status(db, actor, target.id, changed.revision, "disabled", apply=True)
    assert disabled.outcome == OutcomeCode.SUCCESS and session.revoked_at is not None
    reactivated = set_user_status(db, actor, target.id, disabled.revision, "active", apply=True)
    assert reactivated.outcome == OutcomeCode.SUCCESS


def test_invalid_user_create_can_be_corrected_without_reentering_values(client, csrf, db_factory, db):
    sign_in(client, csrf, email="admin@example.test")
    group = db.query(__import__("auth_ingress.models", fromlist=["Group"]).Group).filter_by(name="staff").one()
    invalid = client.post(
        "/admin/users/preview",
        data={
            "csrf": csrf,
            "email": "bad-email",
            "display_name": "New User",
            "status": "active",
            "group_ids": str(group.id),
        },
    )
    assert invalid.status_code == 400
    assert 'name="display_name" value="New User"' in invalid.text
    assert f'name="group_ids" value="{group.id}" checked' in invalid.text
    assert "Temporary password" not in invalid.text

    preview = client.post(
        "/admin/users/preview",
        data={
            "csrf": csrf,
            "email": "new@example.test",
            "display_name": "New User",
            "status": "active",
            "group_ids": str(group.id),
        },
    )
    assert preview.status_code == 200
    assert "Preview user creation" in preview.text
    confirm = client.post(
        "/admin/users/confirm",
        data={
            "csrf": csrf,
            "email": "new@example.test",
            "display_name": "New User",
            "status": "active",
            "group_ids": str(group.id),
        },
    )
    assert confirm.status_code == 201
    assert "Temporary password" in confirm.text
    with db_factory() as check:
        assert check.query(User).filter_by(email="new@example.test").one()
