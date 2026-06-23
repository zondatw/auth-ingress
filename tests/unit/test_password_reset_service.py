from datetime import timedelta

import pytest

from auth_entry_portal.models import User
from auth_entry_portal.services.password_reset_service import complete_reset, encode_reset_cookie, initiate_reset, utcnow
from auth_entry_portal.services.user_management_types import ManagementError
from tests.fixtures.recovery_delivery import CapturingRecoveryDelivery


def test_reset_is_digest_only_single_use_and_supersedes(db, settings):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    target = db.query(User).filter_by(email="member@example.test").one()
    delivery = CapturingRecoveryDelivery()
    first = initiate_reset(db, actor, target, settings, delivery, "https://portal.test")
    second = initiate_reset(db, actor, target, settings, delivery, "https://portal.test")
    assert first.token_digest != second.token_digest
    assert first.invalidated_at is not None
    raw = delivery.messages[-1][1].split("token=", 1)[1]
    assert raw not in second.token_digest
    cookie = encode_reset_cookie(raw, settings)
    complete_reset(db, cookie, "new-correct-password", settings)
    with pytest.raises(ManagementError):
        complete_reset(db, cookie, "another-correct-password", settings)


def test_expired_reset_is_rejected(db, settings):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    target = db.query(User).filter_by(email="member@example.test").one()
    delivery = CapturingRecoveryDelivery()
    request = initiate_reset(db, actor, target, settings, delivery, "https://portal.test")
    request.expires_at = utcnow() - timedelta(seconds=1); db.commit()
    raw = delivery.messages[-1][1].split("token=", 1)[1]
    with pytest.raises(ManagementError):
        complete_reset(db, encode_reset_cookie(raw, settings), "new-correct-password", settings)
