import pytest
from starlette.testclient import TestClient

from main import app
from db.database import get_db

@pytest.fixture
def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
@pytest.mark.skip
async def test_websocket(client, data_in):
    user_id = data_in["member"].user_id
    guild_id = data_in["member"].guild_id

    with client.websocket_connect(f"/api/v1/chat/ws/guild/{guild_id}/{user_id}") as websocket:
        history = websocket.receive_json()
        assert history["type"] == "history"

        websocket.send_json({
            "type": "message",
            "content": "Hello from test!"
        })

        msg = websocket.receive_json()
        assert msg["content"] == "Hello from test!"
        assert msg["user_name"] == "TestUser"


@pytest.mark.skip
def test_websocket_error(client):
    user_id = 1
    guild_id = 1
    with client.websocket_connect(f"/api/v1/chat/ws/guild/{guild_id}/{user_id}") as websocket:
        history = websocket.receive_json()
        assert history["type"] == "error"

