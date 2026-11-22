
from typing import Any, Sequence

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    ExternalServiceException,
    ExternalServiceTimeoutException,
)
from app.llm.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
)


class OpenAIProvider(BaseLLMProvider):
    """Asynchronous OpenAI implementation of the LLM provider contract."""

    def __init__(
        self,
        settings: Settings | None = None,
        client: Any | None = None,
    ) -> None:
        self._settings = settings or get_settings()

        # An injected client allows unit tests to mock API calls.
        if client is not None:
            self._client = client
        else:
            api_key = self._settings.openai_api_key

            if api_key is None:
                raise ExternalServiceException()

            self._client = AsyncOpenAI(
                api_key=api_key.get_secret_value(),
                timeout=self._settings.llm_timeout_seconds,
            )

    async def generate(
        self,
        messages: Sequence[LLMMessage],
        *,
        temperature: float = 0.2,
        max_output_tokens: int = 800,
    ) -> LLMResponse:
        """Generate a response using the OpenAI Responses API."""

        system_messages = [
            message.content
            for message in messages
            if message.role == "system"
        ]

        input_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
            if message.role != "system"
        ]

        request_arguments: dict[str, Any] = {
            "model": self._settings.openai_model,
            "input": input_messages,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }

        if system_messages:
            request_arguments["instructions"] = "\n\n".join(
                system_messages
            )

        try:
            response = await self._client.responses.create(
                **request_arguments
            )

            usage = getattr(response, "usage", None)

            return LLMResponse(
                content=response.output_text,
                provider="openai",
                model=self._settings.openai_model,
                input_tokens=(
                    getattr(usage, "input_tokens", None)
                    if usage is not None
                    else None
                ),
                output_tokens=(
                    getattr(usage, "output_tokens", None)
                    if usage is not None
                    else None
                ),
            )

        except APITimeoutError:
            raise ExternalServiceTimeoutException() from None

        except (
            AuthenticationError,
            RateLimitError,
            APIConnectionError,
            APIStatusError,
            OpenAIError,
        ):
            raise ExternalServiceException() from None

    async def close(self) -> None:
        """Close the asynchronous OpenAI client."""
        await self._client.close()
