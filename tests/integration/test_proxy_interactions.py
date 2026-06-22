import hashlib

from tests.conftest import launch_proxy


def test_form_json_and_repeated_query_interactions(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    form = client.post(origin + "/form", data={"value": "updated"})
    assert form.status_code == 200
    assert "updated" in form.text
    action = client.post(origin + "/api/data?item=one&item=two", content=b'{"ok":true}', headers={"Content-Type": "application/json"})
    assert action.json()["items"] == ["one", "two"]
    assert action.json()["body"] == '{"ok":true}'


def test_streamed_upload_download_checksums_and_range(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    upload_content = b"upload-block" * 100_000
    upload = client.post(origin + "/upload", content=upload_content)
    assert upload.status_code == 200
    assert upload.json() == {"size": len(upload_content), "sha256": hashlib.sha256(upload_content).hexdigest()}
    download = client.get(origin + "/download?size=2097152")
    assert len(download.content) == 2 * 1024 * 1024
    assert download.headers["etag"] == '"fixture"'
    partial = client.get(origin + "/range", headers={"Range": "bytes=2-5"})
    assert partial.status_code == 206
    assert partial.headers["accept-ranges"] == "bytes"
