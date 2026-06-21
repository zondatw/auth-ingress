from tests.conftest import sign_in


def test_preserves_requested_service_and_enters(client, csrf):
    response = client.get("/services/demo", follow_redirects=False)
    assert response.status_code == 302
    assert "return_to=/services/demo" in response.headers["location"]
    response = sign_in(client, csrf, return_to="/services/demo")
    assert response.headers["location"] == "/services/demo"
    assert "Protected service reached" in client.get("/services/demo").text


def test_lists_only_allowed_services(client, csrf):
    sign_in(client, csrf)
    response = client.get("/")
    assert "Demo Service" in response.text
    assert "Offline" not in response.text


def test_empty_state_for_user_without_memberships(client, csrf):
    sign_in(client, csrf, email="outsider@example.test")
    response = client.get("/")
    assert "No services available" in response.text

