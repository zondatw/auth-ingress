from sqlalchemy import delete, select

from auth_entry_portal.models import AccessRule, ServiceEntry
from tests.conftest import sign_in


def test_permission_change_is_effective_immediately(client, csrf, db_factory):
    sign_in(client, csrf)
    assert client.get("/services/demo").status_code == 200
    with db_factory() as db:
        service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == "demo"))
        db.execute(delete(AccessRule).where(AccessRule.service_entry_id == service.id))
        db.commit()
    assert client.get("/services/demo").status_code == 403


def test_unknown_disabled_and_unavailable_are_clear(client, csrf):
    sign_in(client, csrf)
    assert "not found" in client.get("/services/not-real").text.lower()
    assert "currently unavailable" in client.get("/services/offline").text.lower()
    assert "could not be reached" in client.get("/services/broken").text.lower()

