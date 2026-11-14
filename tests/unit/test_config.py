import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_default_settings():
    settings = Settings(_env_file=None)

    assert settings.app_name == "Agentic AI Chatbot"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"


def test_settings_can_be_overridden():
    settings = Settings(
        _env_file=None,
        app_name="Test Chatbot",
        environment="testing",
        debug=True,
    )

    assert settings.app_name == "Test Chatbot"
    assert settings.environment == "testing"
    assert settings.debug is True


def test_timeout_validation():
    settings = Settings(
        _env_file=None,
        request_timeout_seconds=60,
    )

    assert settings.request_timeout_seconds == 60

@pytest.mark.parametrize(
    "origins",
    [
        ["http://localhost:5173"],
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        ["https://example.com"],
        [],
    ],
)
def test_valid_allowed_origins(origins):
    settings = Settings(
        _env_file=None,
        allowed_origins=origins,
    )

    assert settings.allowed_origins == origins


def test_default_allowed_origins():
    settings = Settings(_env_file=None)

    assert settings.allowed_origins == [
        "http://localhost:5173"
    ]


@pytest.mark.parametrize(
    "origins",
    [
        [123],
        ["http://localhost:5173", 123],
        [None],
    ],
)
def test_invalid_allowed_origins(origins):
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            allowed_origins=origins,
        )
