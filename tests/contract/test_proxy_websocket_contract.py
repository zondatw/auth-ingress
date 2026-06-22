from tests.conftest import launch_proxy


def test_text_binary_subprotocol_and_query_contract(client, csrf, proxy_service):
    launch_proxy(client, csrf)
    with client.websocket_connect("ws://demo.apps.test/ws?channel=one", subprotocols=["fixture"]) as websocket:
        assert websocket.accepted_subprotocol == "fixture"
        websocket.send_text("hello")
        assert websocket.receive_text() == "hello"
        websocket.send_bytes(b"\x00\x01proxy")
        assert websocket.receive_bytes() == b"\x00\x01proxy"


def test_clean_websocket_close_contract(client, csrf, proxy_service):
    launch_proxy(client, csrf)
    with client.websocket_connect("ws://demo.apps.test/ws") as websocket:
        websocket.send_text("done")
        assert websocket.receive_text() == "done"
