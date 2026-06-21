from time import perf_counter

from tests.conftest import sign_in


def test_local_portal_responses_complete_under_one_second(client, csrf):
    started = perf_counter()
    sign_in(client, csrf)
    response = client.get("/")
    assert response.status_code == 200
    assert perf_counter() - started < 1.0


def test_authorized_entry_completes_well_under_sixty_seconds(client, csrf):
    started = perf_counter()
    sign_in(client, csrf, return_to="/services/demo")
    assert client.get("/services/demo").status_code == 200
    assert perf_counter() - started < 60.0

