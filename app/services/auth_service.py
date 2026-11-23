
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
)
from app.schemas.auth import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.user_store import user_store


password_hasher = PasswordHash.recommended()


class AuthService:
    """Handles user registration, authentication, and JWT validation."""

    def register(self, request: RegisterRequest) -> UserResponse:
        email = str(request.email).strip().lower()

        if user_store.get_by_email(email):
            raise UserAlreadyExistsException()

        hashed_password = password_hasher.hash(request.password)

        try:
            return user_store.create_user(
                email=email,
                hashed_password=hashed_password,
            )
        except ValueError as exc:
            raise UserAlreadyExistsException() from exc

    def login(self, email: str, password: str) -> TokenResponse:
        email = email.strip().lower()
        user = user_store.get_by_email(email)

        if user is None or not password_hasher.verify(
            password,
            user["hashed_password"],
        ):
            raise InvalidCredentialsException()

        settings = get_settings()

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

        payload = {
            "sub": user["id"],
            "role": user["role"],
            "iat": now,
            "exp": expires_at,
        }

        token = jwt.encode(
            payload,
            settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )

        return TokenResponse(
            access_token=token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    def get_user_from_token(self, token: str) -> UserResponse:
        """Validate a JWT and return its associated user."""

        settings = get_settings()

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key.get_secret_value(),
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenException() from exc

        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            raise InvalidTokenException()

        user = user_store.get_by_id(user_id)

        if user is None:
            raise InvalidTokenException()

        return user_store.to_user_response(user)


auth_service = AuthService()
