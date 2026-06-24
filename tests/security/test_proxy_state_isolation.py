from sqlalchemy import select

from auth_ingress.models import AccessRule, Group, ServiceEntry
from tests.conftest import launch_proxy


def test_reserved_cookies_are_not_forwarded_or_overwritten(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    first = client.get(origin + "/cookie")
    assert first.json()["state"] is None
    assert "auth_portal_service=forged" not in first.headers.get("set-cookie", "")
    second = client.get(origin + "/cookie")
    assert second.json()["state"] == "fixture"
    assert client.get(origin + "/").status_code == 200


def test_same_named_app_cookie_is_isolated_by_service_host(client, csrf, proxy_service, db_factory):
    first_origin = launch_proxy(client, csrf)
    client.get(first_origin + "/cookie")
    with db_factory() as db:
        staff = db.scalar(select(Group).where(Group.name == "staff"))
        second = ServiceEntry(slug="second", display_name="Second", destination=proxy_service, proxy_enabled=True)
        db.add(second)
        db.flush()
        db.add(AccessRule(service_entry_id=second.id, group_id=staff.id))
        db.commit()
    launch = client.get("http://testserver/services/second", follow_redirects=False)
    bootstrap = client.get(launch.headers["location"], follow_redirects=False)
    assert bootstrap.status_code == 302
    second_origin = launch.headers["location"].split("/__portal/", 1)[0]
    assert client.get(second_origin + "/cookie").json()["state"] is None
    assert client.get(first_origin + "/cookie").json()["state"] == "fixture"


def test_external_redirect_and_later_permission_change_are_denied(client, csrf, proxy_service, db_factory):
    origin = launch_proxy(client, csrf)
    assert client.get(origin + "/redirect/external", follow_redirects=False).status_code == 502
    with db_factory() as db:
        service = db.scalar(select(ServiceEntry).where(ServiceEntry.slug == "demo"))
        db.query(AccessRule).filter(AccessRule.service_entry_id == service.id).delete()
        db.commit()
    denied = client.get(origin + "/api/data", follow_redirects=False)
    assert denied.status_code == 302
    assert denied.headers["location"] == "http://testserver/services/demo"
