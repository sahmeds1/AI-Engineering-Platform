
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import SecretStr

import app.llm.openai_provider as provider_module

from app.core.config import Settings
from app.core.exceptions import (
    ExternalServiceException,
    ExternalServiceTimeoutException,
)
from app.llm.base import LLMMessage
from app.llm.openai_provider import OpenAIProvider


@pytest.fixture
def settings():
    return Settings(
        openai_api_key=SecretStr("test-api-key"),
        openai_model="gpt-4.1-mini",
    )


@pytest.fixture
def mock_client():
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=AsyncMock()
        ),
        close=AsyncMock(),
    )
    return client


@pytest.mark.asyncio
async def test_generate_returns_standard_llm_response(
    settings,
    mock_client,
):
    mock_client.responses.create.return_value = SimpleNamespace(
        output_text="Hello from the mocked OpenAI API.",
        usage=SimpleNamespace(
            input_tokens=12,
            output_tokens=8,
        ),
    )

    provider = OpenAIProvider(
        settings=settings,
        client=mock_client,
    )

    result = await provider.generate(
        [
            LLMMessage(
                role="system",
                content="You are a helpful assistant.",
            ),
            LLMMessage(
                role="user",
                content="Explain asynchronous Python.",
            ),
        ]
    )

    assert result.content == "Hello from the mocked OpenAI API."
    assert result.provider == "openai"
    assert result.model == "gpt-4.1-mini"
    assert result.input_tokens == 12
    assert result.output_tokens == 8

    mock_client.responses.create.assert_awaited_once()

    request = mock_client.responses.create.await_args.kwargs

    assert request["instructions"] == "You are a helpful assistant."
    assert request["input"][0]["role"] == "user"
    assert request["temperature"] == 0.2
    assert request["max_output_tokens"] == 800


@pytest.mark.asyncio
async def test_generate_handles_timeout(
    settings,
    mock_client,
    monkeypatch,
):
    class FakeTimeoutError(Exception):
        pass

    monkeypatch.setattr(
        provider_module,
        "APITimeoutError",
        FakeTimeoutError,
    )

    mock_client.responses.create.side_effect = FakeTimeoutError()

    provider = OpenAIProvider(
        settings=settings,
        client=mock_client,
    )

    with pytest.raises(ExternalServiceTimeoutException):
        await provider.generate(
            [LLMMessage(role="user", content="Hello")]
        )


@pytest.mark.asyncio
async def test_generate_handles_authentication_failure(
    settings,
    mock_client,
    monkeypatch,
):
    class FakeAuthenticationError(Exception):
        pass

    monkeypatch.setattr(
        provider_module,
        "AuthenticationError",
        FakeAuthenticationError,
    )

    mock_client.responses.create.side_effect = FakeAuthenticationError()

    provider = OpenAIProvider(
        settings=settings,
        client=mock_client,
    )

    with pytest.raises(ExternalServiceException):
        await provider.generate(
            [LLMMessage(role="user", content="Hello")]
        )


@pytest.mark.asyncio
async def test_generate_handles_rate_limit(
    settings,
    mock_client,
    monkeypatch,
):
    class FakeRateLimitError(Exception):
        pass

    monkeypatch.setattr(
        provider_module,
        "RateLimitError",
        FakeRateLimitError,
    )

    mock_client.responses.create.side_effect = FakeRateLimitError()

    provider = OpenAIProvider(
        settings=settings,
        client=mock_client,
    )

    with pytest.raises(ExternalServiceException):
        await provider.generate(
            [LLMMessage(role="user", content="Hello")]
        )


@pytest.mark.asyncio
async def test_provider_closes_client(
    settings,
    mock_client,
):
    provider = OpenAIProvider(
        settings=settings,
        client=mock_client,
    )

    await provider.close()

    mock_client.close.assert_awaited_once()


def test_provider_rejects_missing_api_key():
    settings = Settings(openai_api_key=None)

    with pytest.raises(ExternalServiceException):
        OpenAIProvider(settings=settings)
