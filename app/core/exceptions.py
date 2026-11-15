
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
