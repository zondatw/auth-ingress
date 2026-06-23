from auth_entry_portal.models import AccessRule, Group, GroupMembership, ServiceEntry, User
from auth_entry_portal.services.access_service import effective_access_for_user


def test_effective_access_explains_overlapping_groups(db):
    user = db.query(User).filter_by(email="member@example.test").one()
    service = db.query(ServiceEntry).filter_by(slug="demo").one()
    extra = Group(name="engineering", description="Engineering")
    db.add(extra); db.flush()
    db.add_all([GroupMembership(user_id=user.id, group_id=extra.id), AccessRule(service_entry_id=service.id, group_id=extra.id)])
    db.commit()
    result = next(item for item in effective_access_for_user(db, user) if item["service_slug"] == "demo")
    assert result["granting_groups"] == ["engineering", "staff"]
    assert result["currently_usable"] is True
    user.status = "disabled"; db.commit()
    result = next(item for item in effective_access_for_user(db, user) if item["service_slug"] == "demo")
    assert result["policy_granted"] is True and result["currently_usable"] is False
