
from app.core.config import Settings, get_settings
from app.core.exceptions import ExternalServiceException
from app.llm.base import BaseLLMProvider
from app.llm.openai_provider import OpenAIProvider


def create_llm_provider(
    settings: Settings | None = None,
) -> BaseLLMProvider:
    """
    Create an LLM provider based on application configuration.

    Currently supported:
        - openai

    Future providers:
        - bedrock
        - azure_openai
    """

    settings = settings or get_settings()

    if settings.llm_provider == "openai":
        return OpenAIProvider(settings=settings)

    # Do not silently fall back to another provider.
    # Unsupported configurations must fail safely.
    raise ExternalServiceException()
