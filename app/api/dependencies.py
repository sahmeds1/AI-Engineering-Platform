
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.core.exceptions import InvalidTokenException
from app.schemas.auth import UserResponse
from app.services.auth_service import auth_service
from app.services.chat_service import ChatService


# Existing chat service dependency
def get_chat_service() -> ChatService:
    return ChatService()


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
            from fastapi import HTTPException

            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker
