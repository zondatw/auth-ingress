from auth_ingress.models import User
from auth_ingress.services.password_reset_service import initiate_reset
from tests.conftest import sign_in
from tests.fixtures.recovery_delivery import CapturingRecoveryDelivery


def test_reset_exchange_redirects_to_clean_url_and_never_renders_token(client, db, settings):
    actor = db.query(User).filter_by(email="admin@example.test").one()
    target = db.query(User).filter_by(email="member@example.test").one()
    delivery = CapturingRecoveryDelivery()
    initiate_reset(db, actor, target, settings, delivery, "http://testserver")
    link = delivery.messages[-1][1]
    token = link.split("token=", 1)[1]
    response = client.get(f"/reset-password?token={token}", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "/reset-password"
    page = client.get("/reset-password")
    assert token not in page.text
    assert page.headers["referrer-policy"] == "no-referrer"


def test_reset_admin_route_never_returns_secret(client, csrf, db):
    sign_in(client, csrf, email="admin@example.test")
    target = db.query(User).filter_by(email="member@example.test").one()
    response = client.post(f"/admin/users/{target.id}/reset-password", data={"csrf": csrf, "expected_revision": target.revision, "confirm": "true"})
    assert "token=" not in response.text
