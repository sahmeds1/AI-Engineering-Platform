
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Sequence


MessageRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class LLMMessage:
    """Provider-independent representation of a chat message."""

    role: MessageRole
    content: str


@dataclass(frozen=True)
class LLMResponse:
    """Standard response returned by any LLM provider."""

    content: str
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class BaseLLMProvider(ABC):
    """Contract that every LLM provider must implement."""

    @abstractmethod
    async def generate(
        self,
        messages: Sequence[LLMMessage],
        *,
        temperature: float = 0.2,
        max_output_tokens: int = 800,
    ) -> LLMResponse:
        """Generate a response using the configured LLM."""
        raise NotImplementedError
