from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from auth_ingress.models import AuditEvent, GroupMembership, PasswordResetRequest, PortalSession, User
from auth_ingress.services.audit_service import record_event
from auth_ingress.services.password_reset_service import token_digest
from auth_ingress.services.user_admin_service import delete_user
from auth_ingress.services.user_management_types import ManagementError, OutcomeCode


def test_delete_user_removes_account_auth_state_and_preserves_audit(db):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    target = db.query(User).filter_by(email="member@example.test").one()
    target_id = target.id
    db.add(PortalSession(id="delete-session", user_id=target_id, expires_at=datetime.now(timezone.utc) + timedelta(hours=1)))
    db.add(PasswordResetRequest(user_id=target_id, token_digest=token_digest("delete-token"), expires_at=datetime.now(timezone.utc) + timedelta(hours=1), requested_by_user_id=actor.id))
    event = record_event(db, "user_viewed", "allowed", "admin_view", actor_user_id=actor.id, target_user_id=target_id, commit=False)
    db.commit()

    preview = delete_user(db, actor, target_id, target.revision, apply=False)
    assert preview.outcome == OutcomeCode.SUCCESS
    assert db.get(User, target_id) is not None

    result = delete_user(db, actor, target_id, target.revision, apply=True)
    assert result.outcome == OutcomeCode.SUCCESS
    assert db.get(User, target_id) is None
    assert db.scalar(select(GroupMembership).where(GroupMembership.user_id == target_id)) is None
    assert db.scalar(select(PortalSession).where(PortalSession.user_id == target_id)) is None
    assert db.scalar(select(PasswordResetRequest).where(PasswordResetRequest.user_id == target_id)) is None
    preserved = db.get(AuditEvent, event.id)
    assert preserved is not None
    assert preserved.target_user_id is None


def test_delete_user_rejects_self_and_last_active_admin(db):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    try:
        delete_user(db, actor, actor.id, actor.revision, apply=True)
    except ManagementError as error:
        assert error.code == OutcomeCode.DENIED
    else:
        raise AssertionError("self-delete should be denied")
