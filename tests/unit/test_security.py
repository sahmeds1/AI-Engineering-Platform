
import logging

import pytest
from fastapi import HTTPException
from pydantic import SecretStr

from app.core.security import redact_secrets
from app.core.logging_config import SecretRedactionFilter
from app.core.exceptions import handle_llm_provider_error


def test_openai_key_is_redacted():
    message = "Request failed with sk-123456789abcdef"

    result = redact_secrets(message)

    assert "sk-123456789abcdef" not in result
    assert "[REDACTED]" in result


def test_bearer_token_is_redacted():
    message = "Authorization: Bearer abc123.secret-token"

    result = redact_secrets(message)

    assert "abc123.secret-token" not in result
    assert "[REDACTED]" in result


def test_api_key_assignment_is_redacted():
    message = "api_key=super-secret-value"

    result = redact_secrets(message)

    assert "super-secret-value" not in result
    assert "[REDACTED]" in result


def test_password_is_redacted():
    message = "password=my-secret-password"

    result = redact_secrets(message)

    assert "my-secret-password" not in result
    assert "[REDACTED]" in result


def test_safe_message_remains_unchanged():
    message = "Application started successfully"

    assert redact_secrets(message) == message


def test_logging_filter_redacts_secret():
    log_filter = SecretRedactionFilter()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname=__file__,
        lineno=10,
        msg="Authentication failed: api_key=secret123",
        args=(),
        exc_info=None,
    )

    log_filter.filter(record)

    assert "secret123" not in record.getMessage()
    assert "[REDACTED]" in record.getMessage()


def test_provider_error_returns_generic_message(caplog):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(HTTPException) as error:
            handle_llm_provider_error()

    assert error.value.status_code == 502
    assert error.value.detail == (
        "The AI service is temporarily unavailable."
    )
    assert "Internal details withheld" in caplog.text
    assert "secret123" not in caplog.text


def test_secretstr_masks_value():
    secret = SecretStr("my-private-api-key")

    assert "my-private-api-key" not in str(secret)
    assert secret.get_secret_value() == "my-private-api-key"
