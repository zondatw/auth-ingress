import hashlib

from tests.conftest import launch_proxy


def test_methods_query_and_body_contract(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]:
        response = client.request(method, origin + "/api/data?item=a&item=b", content=b"payload")
        assert response.status_code == 200
        assert response.json() == {"method": method, "items": ["a", "b"], "body": "payload"}


def test_download_range_cookie_and_redirect_contract(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    download = client.get(origin + "/download?size=4096")
    assert download.status_code == 200
    assert len(download.content) == 4096
    assert 'filename="fixture.bin"' in download.headers["content-disposition"]
    assert hashlib.sha256(download.content).hexdigest()
    partial = client.get(origin + "/range", headers={"Range": "bytes=2-5"})
    assert partial.status_code == 206
    assert partial.content == b"2345"
    assert partial.headers["content-range"] == "bytes 2-5/10"
    cookie = client.get(origin + "/cookie")
    assert cookie.status_code == 200
    assert "app_state=fixture" in cookie.headers.get("set-cookie", "")
    assert "auth_portal_service=forged" not in cookie.headers.get("set-cookie", "")
    internal = client.get(origin + "/redirect/internal", follow_redirects=False)
    assert internal.status_code == 302
    assert internal.headers["location"] == "/nested/page"
    absolute = client.get(origin + "/redirect/absolute", follow_redirects=False)
    assert absolute.status_code == 302
    assert absolute.headers["location"] == origin + "/nested/page"
    assert client.get(origin + "/redirect/external", follow_redirects=False).status_code == 502
