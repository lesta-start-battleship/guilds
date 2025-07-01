def test_websocket(client):
    user_id = 1
    guild_id = 1
    with client.websocket_connect(f"/api/v1/ws/guild/{guild_id}/{user_id}") as websocket:
        history = websocket.receive_json()
        assert history["type"] == "history"

        websocket.send_json({
            "user_id": 42,
            "user_name": "TestUser",
            "content": "Hello from test!"
        })

        msg = websocket.receive_json()
        assert msg["content"] == "Hello from test!"
        assert msg["user_name"] == "TestUser"
