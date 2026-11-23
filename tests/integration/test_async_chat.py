
import asyncio
from typing import Sequence

import httpx
import pytest

from app.api.dependencies import get_llm_provider
from app.llm.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
)



class FakeLLMProvider(BaseLLMProvider):
    """Fake provider for integration testing without API calls."""

    def __init__(self, delay: float = 0.05) -> None:
        self.delay = delay
        self.active_requests = 0
        self.max_concurrent_requests = 0

    async def generate(
        self,
        messages: Sequence[LLMMessage],
        *,
        temperature: float = 0.2,
        max_output_tokens: int = 800,
    ) -> LLMResponse:

        self.active_requests += 1

        self.max_concurrent_requests = max(
            self.max_concurrent_requests,
            self.active_requests,
        )

        try:
            await asyncio.sleep(self.delay)

            last_message = messages[-1].content

            return LLMResponse(
                content=f"Fake AI response: {last_message}",
                provider="fake",
                model="fake-model",
            )
        finally:
            self.active_requests -= 1


@pytest.mark.asyncio
async def test_two_chat_requests_can_run_concurrently(authenticated_app):

    fake_provider = FakeLLMProvider(delay=0.1)

    authenticated_app.dependency_overrides[get_llm_provider] = (
        lambda: fake_provider
    )

    try:
        transport = httpx.ASGITransport(app=authenticated_app)

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

        assert (
            "First request"
            in responses[0].json()["response"]
        )

        assert (
            "Second request"
            in responses[1].json()["response"]
        )

        assert fake_provider.max_concurrent_requests == 2

    finally:
        authenticated_app.dependency_overrides.pop(
            get_llm_provider,
            None,
        )


@pytest.mark.asyncio
async def test_llm_timeout_returns_504(monkeypatch, authenticated_app):

    fake_provider = FakeLLMProvider(delay=0.1)

    authenticated_app.dependency_overrides[get_llm_provider] = (
    lambda: fake_provider
)

    monkeypatch.setattr(
        "app.services.chat_service.get_settings",
        lambda: type(
            "TestSettings",
            (),
            {
                "max_conversation_history": 20,
                "llm_timeout_seconds": 0.01,
            },
        )(),
    )

    try:
        transport = httpx.ASGITransport(app=authenticated_app)

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

        assert (
            data["error"]["code"]
            == "EXTERNAL_SERVICE_TIMEOUT"
        )

        assert data["error"]["request_id"]

        assert (
            "request_id"
            not in data["error"]["message"]
        )

    finally:
        authenticated_app.dependency_overrides.pop(
    get_llm_provider,
    None,
)
