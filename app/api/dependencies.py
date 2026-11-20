
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.core.exceptions import InvalidTokenException
from app.schemas.auth import TokenClaims
from app.services.auth_service import auth_service
from app.services.chat_service import ChatService


def get_chat_service() -> ChatService:
    """Provide a ChatService instance."""
    return ChatService()


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> TokenClaims:
    if credentials is None:
        raise InvalidTokenException()

    return auth_service.get_user_from_token(credentials.credentials)
