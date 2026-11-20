
import logging

from fastapi import HTTPException


logger = logging.getLogger(__name__)


def handle_llm_provider_error() -> None:
    """
    Log a safe error and return a generic API response.
    """

    logger.error(
        "LLM provider request failed. "
        "Internal details withheld."
    )

    raise HTTPException(
        status_code=502,
        detail="The AI service is temporarily unavailable.",
    )


class ApplicationException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code

        super().__init__(message)


class ConversationNotFoundException(ApplicationException):
    """Raised when a conversation does not exist."""

    def __init__(self) -> None:
        super().__init__(
            code="CONVERSATION_NOT_FOUND",
            message="Conversation not found.",
            status_code=404,
        )


class ExternalServiceException(ApplicationException):
    """Raised when an external service fails."""

    def __init__(self) -> None:
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message="An external service is temporarily unavailable.",
            status_code=503,
        )

class ExternalServiceTimeoutException(ApplicationException):
    def __init__(self) -> None:
        super().__init__(
            code="EXTERNAL_SERVICE_TIMEOUT",
            message="The external service did not respond in time.",
            status_code=504,
        )


class InvalidTokenException(ApplicationException):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_TOKEN",
            message="Authentication is required or the token is invalid.",
            status_code=401,
        )