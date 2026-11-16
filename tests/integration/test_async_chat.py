import asyncio
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.chat_service import ChatService


client = TestClient(app)


@pytest.mark.asyncio
async def test_two_chat_requests_can_run_concurrently():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        responses = await asyncio.gather(
            async_client.post(
                "/api/v1/chat",
                json={"message": "First request"},
            ),
            async_client.post(
                "/api/v1/chat",
                json={"message": "Second request"},
            ),
        )

    assert responses[0].status_code == 200
    assert responses[1].status_code == 200

    assert "First request" in responses[0].json()["response"]
    assert "Second request" in responses[1].json()["response"]


@pytest.mark.asyncio
async def test_external_service_timeout_returns_504(monkeypatch):
    async def slow_service(self, message: str) -> str:
        await asyncio.sleep(0.1)
        return "This response should not be returned"

    monkeypatch.setattr(
        ChatService,
        "_simulate_external_service",
        slow_service,
    )

    monkeypatch.setattr(
        "app.services.chat_service.get_settings",
        lambda: SimpleNamespace(external_service_timeout_seconds=0.01),
    )

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        response = await async_client.post(
            "/api/v1/chat",
            json={"message": "Test timeout"},
        )

    assert response.status_code == 504

    data = response.json()
    assert data["error"]["code"] == "EXTERNAL_SERVICE_TIMEOUT"
    assert data["error"]["request_id"]
    assert "request_id" not in data["error"]["message"]