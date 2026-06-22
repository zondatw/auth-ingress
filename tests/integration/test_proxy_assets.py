from tests.conftest import launch_proxy


def test_complete_assets_and_content_types(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    expected = {
        "/": "text/html",
        "/static/style.css": "text/css",
        "/static/relative.css": "text/css",
        "/static/app.js": "application/javascript",
        "/static/logo.svg": "image/svg+xml",
        "/static/font.woff2": "font/woff2",
        "/document.txt": "text/plain",
    }
    for path, content_type in expected.items():
        response = client.get(origin + path)
        assert response.status_code == 200
        assert content_type in response.headers["content-type"]


def test_nested_refresh_head_and_missing_resource(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    nested = client.get(origin + "/nested/page")
    assert nested.status_code == 200
    assert "Nested Page" in nested.text
    head = client.head(origin + "/static/style.css")
    assert head.status_code == 200
    assert head.content == b""
    assert client.get(origin + "/missing").status_code == 404
