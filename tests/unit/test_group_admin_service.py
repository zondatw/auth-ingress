import pytest

from auth_ingress.models import AccessRule, Group, GroupMembership, ServiceEntry, User
from auth_ingress.services.access_service import effective_access_for_user, may_enter
from auth_ingress.services.group_admin_service import (
    GroupValidationError,
    create_group,
    deactivate_group,
    dependency_summary,
    reactivate_group,
    remove_group,
    update_group,
)
from auth_ingress.services.user_management_types import OutcomeCode


def actor(db):
    return db.query(User).filter_by(email="admin@example.test").one()


def test_group_model_normalizes_name_and_defaults_status(db):
    group = Group(name="  Team   One  ", description="Team")
    db.add(group)
    db.commit()

    assert group.name == "Team One"
    assert group.normalized_name == "team one"
    assert group.status == "active"
    assert group.revision == 1


def test_create_update_group_validation_and_stale_revision(db):
    admin = actor(db)
    created = create_group(db, admin, "Platform", "Platform team")
    group = db.get(Group, created.group_id)

    with pytest.raises(GroupValidationError) as duplicate:
        create_group(db, admin, " platform ", "")
    assert duplicate.value.field == "name"

    preview = update_group(db, admin, group.id, group.revision, name="Platform Ops", description="Ops", apply=False)
    assert preview.outcome == OutcomeCode.SUCCESS
    assert db.get(Group, group.id).name == "Platform"

    applied = update_group(db, admin, group.id, group.revision, name="Platform Ops", description="Ops", apply=True)
    assert applied.outcome == OutcomeCode.SUCCESS
    assert db.get(Group, group.id).name == "Platform Ops"

    with pytest.raises(GroupValidationError) as stale:
        update_group(db, admin, group.id, 1, name="Stale", description="", apply=True)
    assert stale.value.code == OutcomeCode.CONFLICT


def test_dependency_summary_and_removal_guardrail(db):
    admin = actor(db)
    staff = db.query(Group).filter_by(name="staff").one()
    summary = dependency_summary(db, staff)

    assert summary.user_count >= 1
    assert summary.service_count >= 1
    with pytest.raises(GroupValidationError):
        remove_group(db, admin, staff.id, staff.revision, apply=True)

    unused = Group(name="unused", description="")
    db.add(unused)
    db.commit()
    result = remove_group(db, admin, unused.id, unused.revision, apply=True)
    assert result.outcome == OutcomeCode.SUCCESS
    assert db.get(Group, unused.id) is None


def test_deactivated_group_stops_and_reactivation_restores_access(db):
    admin = actor(db)
    member = db.query(User).filter_by(email="member@example.test").one()
    service = db.query(ServiceEntry).filter_by(slug="demo").one()
    staff = db.query(Group).filter_by(name="staff").one()

    assert may_enter(db, member, service) is True
    deactivate_group(db, admin, staff.id, staff.revision, apply=True)
    db.refresh(staff)
    assert may_enter(db, member, service) is False
    assert effective_access_for_user(db, member)[0]["currently_usable"] is False
    reactivate_group(db, admin, staff.id, staff.revision, apply=True)
    assert may_enter(db, member, service) is True


def test_last_admin_group_change_is_denied_when_all_admins_depend_on_group(db):
    admin = actor(db)
    admins = db.query(Group).filter_by(name="admins").one()

    with pytest.raises(GroupValidationError) as exc:
        deactivate_group(db, admin, admins.id, admins.revision, apply=True)
    assert exc.value.code == OutcomeCode.DENIED
