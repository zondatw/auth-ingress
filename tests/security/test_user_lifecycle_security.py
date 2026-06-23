import pytest

from auth_entry_portal.models import User
from auth_entry_portal.services.user_admin_service import set_user_status, update_user
from auth_entry_portal.services.user_management_types import ManagementError, OutcomeCode


def test_self_and_last_admin_changes_are_denied(db):
    admin = db.query(User).filter_by(email="admin@example.test").one()
    with pytest.raises(ManagementError) as disabled:
        set_user_status(db, admin, admin.id, admin.revision, "disabled", apply=True)
    assert disabled.value.code == OutcomeCode.DENIED
    with pytest.raises(ManagementError) as demoted:
        update_user(db, admin, admin.id, admin.revision, is_admin=False, apply=True)
    assert demoted.value.code == OutcomeCode.DENIED
    db.refresh(admin)
    assert admin.status == "active" and admin.is_admin is True
