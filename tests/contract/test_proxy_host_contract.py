from tests.conftest import launch_proxy, sign_in


def test_launch_and_bootstrap_contract(client, csrf, proxy_service):
    sign_in(client, csrf)
    launch = client.get("/services/demo", follow_redirects=False)
    assert launch.status_code == 302
    assert launch.headers["location"].startswith("http://demo.apps.test/__portal/bootstrap?ticket=")
    assert launch.headers["cache-control"] == "no-store"
    bootstrap = client.get(launch.headers["location"], follow_redirects=False)
    assert bootstrap.status_code == 302
    assert bootstrap.headers["location"] == "/"
    assert "auth_portal_service=" in bootstrap.headers["set-cookie"]
    assert "HttpOnly" in bootstrap.headers["set-cookie"]


def test_direct_and_unknown_service_host_contract(client, csrf, proxy_service):
    direct = client.get("http://demo.apps.test/", follow_redirects=False)
    assert direct.status_code == 302
    assert direct.headers["location"] == "http://testserver/services/demo"
    assert client.get("http://unknown.apps.test/", follow_redirects=False).status_code == 404
    assert client.get("http://demo.apps.test/__portal/private", follow_redirects=False).status_code in {302, 404}


def test_bootstrapped_host_serves_root(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    response = client.get(f"{origin}/")
    assert response.status_code == 200
    assert "Fixture App" in response.text
