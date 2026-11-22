
import pytest

from app.llm.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
)


class FakeLLMProvider(BaseLLMProvider):
    """Fake provider used for testing the interface."""

    async def generate(
        self,
        messages,
        *,
        temperature=0.2,
        max_output_tokens=800,
    ) -> LLMResponse:
        return LLMResponse(
            content="This is a test response.",
            provider="fake",
            model="fake-model",
            input_tokens=10,
            output_tokens=8,
        )


def test_llm_message_creation():
    message = LLMMessage(
        role="user",
        content="What is an LLM?",
    )

    assert message.role == "user"
    assert message.content == "What is an LLM?"


def test_llm_response_creation():
    response = LLMResponse(
        content="An LLM is a language model.",
        provider="fake",
        model="fake-model",
        input_tokens=10,
        output_tokens=8,
    )

    assert response.provider == "fake"
    assert response.model == "fake-model"
    assert response.input_tokens == 10


def test_provider_implementation():
    provider = FakeLLMProvider()

    assert isinstance(provider, BaseLLMProvider)


def test_incomplete_provider_cannot_be_instantiated():

    class IncompleteProvider(BaseLLMProvider):
        pass

    with pytest.raises(TypeError):
        IncompleteProvider()


@pytest.mark.asyncio
async def test_fake_provider_generates_response():
    provider = FakeLLMProvider()

    messages = [
        LLMMessage(
            role="user",
            content="Explain asynchronous Python",
        )
    ]

    response = await provider.generate(messages)

    assert response.content == "This is a test response."
    assert response.provider == "fake"
    assert response.input_tokens == 10
