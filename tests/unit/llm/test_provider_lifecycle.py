
from unittest.mock import AsyncMock, patch

import pytest

from app.api.dependencies import (
    close_llm_provider,
    get_llm_provider,
)


@pytest.fixture(autouse=True)
def clear_provider_cache():
    get_llm_provider.cache_clear()
    yield
    get_llm_provider.cache_clear()


@pytest.mark.asyncio
async def test_close_provider_does_nothing_when_not_initialized():
    with patch(
        "app.api.dependencies.create_llm_provider"
    ) as factory:

        await close_llm_provider()

        factory.assert_not_called()


@pytest.mark.asyncio
async def test_close_provider_closes_cached_client():
    provider = AsyncMock()

    with patch(
        "app.api.dependencies.create_llm_provider",
        return_value=provider,
    ) as factory:

        cached_provider = get_llm_provider()

        assert cached_provider is provider
        factory.assert_called_once()

        await close_llm_provider()

        provider.close.assert_awaited_once()

        assert get_llm_provider.cache_info().currsize == 0
