
from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.core.exceptions import InvalidTokenException
from app.llm.base import BaseLLMProvider
from app.llm.factory import create_llm_provider
from app.schemas.auth import UserResponse
from app.services.auth_service import auth_service
from app.services.chat_service import ChatService


@lru_cache
def get_llm_provider() -> BaseLLMProvider:
    """Return a shared LLM provider instance."""
    return create_llm_provider()


async def close_llm_provider() -> None:
    """Close the cached LLM provider during application shutdown."""

    # Do not initialize a provider just to close it.
    if get_llm_provider.cache_info().currsize == 0:
        return

    provider = get_llm_provider()

    # Clear the cache so a future lifecycle can initialize a fresh provider.
    get_llm_provider.cache_clear()

    close = getattr(provider, "close", None)

    if close is not None:
        await close()


def get_chat_service(
    provider: BaseLLMProvider = Depends(get_llm_provider),
) -> ChatService:
    """Provide a ChatService with an injected LLM provider."""
    return ChatService(provider=provider)


# JWT Bearer authentication
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> UserResponse:
    if credentials is None:
        raise InvalidTokenException()

    return auth_service.get_user_from_token(
        credentials.credentials
    )


# Role-based authorization
def require_role(*allowed_roles: str):

    def role_checker(
        current_user: UserResponse = Depends(get_current_user),
    ) -> UserResponse:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker
