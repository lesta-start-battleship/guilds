import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport 
from fastapi.testclient import TestClient
from main import app

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
@pytest.mark.asyncio
async def test_war_declaration(client):
    payload1 = {
        "initiator_guild_id": 1,
        "target_guild_id": 2,
        "initiator_owner_id": 1
    }

    payload2 = {
        "initiator_guild_id": 2,
        "target_guild_id": 1,
        "initiator_owner_id": 2
    }

    from asyncio import gather

    res1, res2 = await gather(
        client.post("/api/v1/guild/war/declare", json=payload1),
        client.post("/api/v1/guild/war/declare", json=payload2),
    )

    success = None
    failure = None

    if res1.status_code == 200 and res2.status_code == 400:
        success = res1
        failure = res2
    elif res1.status_code == 400 and res2.status_code == 200:
        success = res2
        failure = res1

    assert success is not None, f"Оба запроса не прошли как ожидалось: {res1.status_code}, {res2.status_code}"
    assert failure.status_code == 400
    assert "already exists" in failure.json()["detail"]
    assert success.json()["status"] == "pending"
