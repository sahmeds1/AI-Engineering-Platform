import jwt
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.exceptions import InvalidTokenException
from app.schemas.auth import TokenClaims


class AuthService:
    def get_user_from_token(self, token: str) -> TokenClaims:
        settings = get_settings()

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key.get_secret_value(),
                algorithms=[settings.jwt_algorithm],
            )
            return TokenClaims.model_validate(payload)
        except (jwt.InvalidTokenError, ValidationError) as exc:
            raise InvalidTokenException() from exc


auth_service = AuthService()