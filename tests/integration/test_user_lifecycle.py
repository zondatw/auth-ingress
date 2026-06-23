from auth_entry_portal.models import PortalSession, User
from auth_entry_portal.services.user_admin_service import create_user, set_user_status, update_user
from auth_entry_portal.services.user_management_types import OutcomeCode
from tests.fixtures.recovery_delivery import CapturingRecoveryDelivery


def test_create_update_disable_and_reactivate(db, settings):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    delivery = CapturingRecoveryDelivery()
    preview = create_user(db, actor, "new@example.test", "New User", "active", False, set(), apply=False, settings=settings, delivery=delivery, base_url="https://portal.test")
    assert preview.outcome == OutcomeCode.SUCCESS and db.query(User).filter_by(email="new@example.test").first() is None
    created = create_user(db, actor, "new@example.test", "New User", "active", False, set(), apply=True, settings=settings, delivery=delivery, base_url="https://portal.test")
    target = db.get(User, created.target_user_id)
    assert target.credential_status == "setup_required" and delivery.messages
    changed = update_user(db, actor, target.id, target.revision, display_name="Renamed", apply=True)
    assert changed.outcome == OutcomeCode.SUCCESS
    session = PortalSession(id="lifecycle-session", user_id=target.id, expires_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc) + __import__("datetime").timedelta(hours=1))
    db.add(session); db.commit()
    disabled = set_user_status(db, actor, target.id, changed.revision, "disabled", apply=True)
    assert disabled.outcome == OutcomeCode.SUCCESS and session.revoked_at is not None
    reactivated = set_user_status(db, actor, target.id, disabled.revision, "active", apply=True)
    assert reactivated.outcome == OutcomeCode.SUCCESS
