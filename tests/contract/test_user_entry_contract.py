from tests.conftest import sign_in


def test_public_and_authenticated_contract(client, csrf):
    assert client.get("/", follow_redirects=False).status_code == 302
    assert client.get("/sign-in").status_code == 200
    response = sign_in(client, csrf)
    assert response.status_code == 302
    assert response.headers["location"] == "/"
    assert client.get("/").status_code == 200
    assert client.get("/services/demo").status_code == 200
    assert client.post("/sign-out", data={"csrf": csrf}, follow_redirects=False).status_code == 302

