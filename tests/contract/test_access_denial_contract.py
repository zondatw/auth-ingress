from tests.conftest import sign_in


def test_denial_status_contract(client, csrf):
    assert client.get("/services/demo", follow_redirects=False).status_code == 302
    sign_in(client, csrf, email="outsider@example.test")
    assert client.get("/services/demo").status_code == 403
    assert client.get("/services/missing").status_code == 404


def test_disabled_and_downstream_unavailable_contract(client, csrf):
    sign_in(client, csrf)
    assert client.get("/services/offline").status_code == 503
    assert client.get("/services/broken").status_code == 503


def test_rate_limit_contract(client, csrf):
    for _ in range(3):
        sign_in(client, csrf, password="wrong-password")
    assert sign_in(client, csrf, password="wrong-password").status_code == 429

