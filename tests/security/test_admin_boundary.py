import pytest

from auth_ingress.services.service_admin_service import ServiceValidationError, validate_destination
from tests.conftest import sign_in


def test_forged_csrf_is_rejected(client, csrf):
    sign_in(client, csrf, email="admin@example.test")
    response = client.post("/admin/services", data={"slug": "x", "display_name": "X", "destination": "mock://x", "status": "enabled", "group_names": "staff", "csrf": "forged"})
    assert response.status_code == 400


@pytest.mark.parametrize("url", ["https://user:pass@app.internal", "https://public.example", "javascript:alert(1)"])
def test_unsafe_destinations_are_rejected(url):
    with pytest.raises(ServiceValidationError):
        validate_destination(url)


def test_missing_group_and_rule_are_rejected(client, csrf):
    sign_in(client, csrf, email="admin@example.test")
    base = {"slug": "x", "display_name": "X", "destination": "mock://x", "status": "enabled", "csrf": csrf}
    assert client.post("/admin/services", data={**base, "group_names": "missing"}).status_code == 400
    assert client.post("/admin/services", data={**base, "group_names": ""}).status_code == 400

