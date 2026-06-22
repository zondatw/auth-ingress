from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from auth_portal.config import Settings
from auth_portal.models import ProxyLaunchTicket
from auth_portal.security.proxy_destination import UnsafeDestination, join_destination, resolve_destination
from auth_portal.security.proxy_host import service_slug_from_host
from tests.conftest import sign_in


def test_ticket_is_one_time_and_service_bound(client, csrf, proxy_service):
    sign_in(client, csrf)
    launch = client.get("/services/demo", follow_redirects=False)
    assert client.get(launch.headers["location"], follow_redirects=False).status_code == 302
    assert client.get(launch.headers["location"], follow_redirects=False).status_code == 403
    mismatched = launch.headers["location"].replace("demo.apps.test", "offline.apps.test")
    assert client.get(mismatched, follow_redirects=False).status_code in {403, 503}


def test_expired_ticket_is_denied(client, csrf, proxy_service, db_factory):
    sign_in(client, csrf)
    launch = client.get("/services/demo", follow_redirects=False)
    with db_factory() as db:
        ticket = db.scalar(select(ProxyLaunchTicket))
        ticket.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert client.get(launch.headers["location"], follow_redirects=False).status_code == 403


@pytest.mark.parametrize("host", ["demo.apps.test", "bad_slug.apps.test", "apps.test", "demo.apps.test:99"])
def test_host_parsing_is_strict(host):
    settings = Settings(proxy_base_domain="apps.test")
    expected = "demo" if host == "demo.apps.test" else None
    assert service_slug_from_host(host, settings) == expected


def test_destination_rejects_public_resolution():
    settings = Settings(trusted_downstream_networks=("127.0.0.0/8",))

    def public_resolver(*args, **kwargs):
        return [(2, 1, 6, "", ("203.0.113.10", 80))]

    with pytest.raises(UnsafeDestination):
        resolve_destination("http://app.internal", settings, resolver=public_resolver)


def test_path_join_rejects_traversal():
    with pytest.raises(UnsafeDestination):
        join_destination("http://127.0.0.1:8001", "/a/../secret")
