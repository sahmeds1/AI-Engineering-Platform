
from unittest.mock import patch

import pytest

from app.core.config import Settings
from app.core.exceptions import ExternalServiceException
from app.llm.factory import create_llm_provider



def test_factory_creates_openai_provider():
    settings = Settings(
        llm_provider="openai",
        openai_api_key="test-api-key",
    )

    with patch(
        "app.llm.factory.OpenAIProvider"
    ) as provider_class:

        provider = create_llm_provider(settings)

        provider_class.assert_called_once_with(
            settings=settings
        )

        assert provider is provider_class.return_value


def test_factory_rejects_unsupported_provider():
    settings = Settings(
        llm_provider="bedrock",
    )

    with pytest.raises(ExternalServiceException):
        create_llm_provider(settings)
