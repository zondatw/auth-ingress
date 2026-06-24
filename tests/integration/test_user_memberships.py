import pytest

from auth_ingress.models import Group, User
from auth_ingress.services.user_admin_service import change_memberships
from auth_ingress.services.user_management_types import ManagementError, OutcomeCode


def test_membership_commit_is_atomic_idempotent_and_revision_checked(db):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    target = db.query(User).filter_by(email="outsider@example.test").one()
    staff = db.query(Group).filter_by(name="staff").one()
    preview = change_memberships(db, actor, target.id, {staff.id}, target.revision, apply=False)
    assert preview.outcome == OutcomeCode.SUCCESS and target.revision == 1
    result = change_memberships(db, actor, target.id, {staff.id}, target.revision, apply=True)
    assert result.outcome == OutcomeCode.SUCCESS and result.revision == 2
    no_change = change_memberships(db, actor, target.id, {staff.id}, 2, apply=True)
    assert no_change.outcome == OutcomeCode.NO_CHANGE
    with pytest.raises(ManagementError) as stale:
        change_memberships(db, actor, target.id, set(), 1, apply=True)
    assert stale.value.code == OutcomeCode.CONFLICT


def test_missing_group_rolls_back_all_memberships(db):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    target = db.query(User).filter_by(email="outsider@example.test").one()
    with pytest.raises(ManagementError) as invalid:
        change_memberships(db, actor, target.id, {99999}, target.revision, apply=True)
    assert invalid.value.code == OutcomeCode.INVALID_INPUT
    assert target.memberships == []
