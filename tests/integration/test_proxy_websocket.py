from tests.conftest import launch_proxy


def test_bidirectional_websocket_relay(client, csrf, proxy_service):
    launch_proxy(client, csrf)
    with client.websocket_connect("ws://demo.apps.test/ws", subprotocols=["fixture"]) as websocket:
        for value in ["first", "second", "third"]:
            websocket.send_text(value)
            assert websocket.receive_text() == value
        for value in [b"first", b"second"]:
            websocket.send_bytes(value)
            assert websocket.receive_bytes() == value
