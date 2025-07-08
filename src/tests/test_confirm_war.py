import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from main import app
from asyncio import gather

@pytest.mark.asyncio
async def test_confirm_two_conflicting_war_requests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Два запроса на подтверждение войны
        req1 = client.post("/api/v1/guild/war/confirm/24", json={"user_id": 1})  # Целевая — гильдия 2
        req2 = client.post("/api/v1/guild/war/confirm/25", json={"user_id": 2})  # Целевая — гильдия 1


        res1, res2 = await gather(req1, req2)

    # Один из них должен быть успешным, второй — 400
    success = None
    failure = None

    if res1.status_code == 200 and res2.status_code == 400:
        success = res1
        failure = res2
    elif res1.status_code == 400 and res2.status_code == 200:
        success = res2
        failure = res1

    assert success is not None, f"Оба запроса провалились:\nres1: {res1.status_code} {res1.text}\nres2: {res2.status_code} {res2.text}"
    assert failure.status_code == 400, f"Ожидался 400, но получили {failure.status_code}. Ответ: {failure.text}"
    assert "already in an active war" in failure.json()["detail"], f"Unexpected error detail: {failure.json()['detail']}"
    assert success.json()["status"] == "active", f"Unexpected success status: {success.json()}"
