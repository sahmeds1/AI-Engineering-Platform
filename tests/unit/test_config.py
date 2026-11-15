
import pytest
from pydantic import ValidationError

from app.core.config import Settings


# --------------------------------------------------
# 1. Default configuration tests
# --------------------------------------------------

def test_default_settings(monkeypatch):
    monkeypatch.delenv("CHATBOT_APP_NAME", raising=False)
    monkeypatch.delenv("CHATBOT_ENVIRONMENT", raising=False)
    monkeypatch.delenv("CHATBOT_API_VERSION", raising=False)
    monkeypatch.delenv(
        "CHATBOT_MAX_CONVERSATION_HISTORY",
        raising=False,
    )
    monkeypatch.delenv("CHATBOT_ALLOWED_ORIGINS", raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_name == "Agentic AI Chatbot"
    assert settings.environment == "development"
    assert settings.api_version == "v1"
    assert settings.max_conversation_history == 20
    assert settings.allowed_origins == [
        "http://localhost:5173"
    ]


# --------------------------------------------------
# 2. Conversation history validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [1, 10, 20, 50, 100],
)
def test_valid_conversation_history(value):
    settings = Settings(
        _env_file=None,
        max_conversation_history=value,
    )

    assert settings.max_conversation_history == value


@pytest.mark.parametrize(
    "value",
    [0, -1, 101, 150],
)
def test_invalid_conversation_history(value):
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            max_conversation_history=value,
        )


# --------------------------------------------------
# 3. Allowed origins validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "origins",
    [
        ["http://localhost:5173"],
        ["https://example.com"],
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        [],
    ],
)
def test_valid_allowed_origins(origins):
    settings = Settings(
        _env_file=None,
        allowed_origins=origins,
    )

    assert settings.allowed_origins == origins


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


# --------------------------------------------------
# 4. Environment variable override tests
# --------------------------------------------------

def test_environment_variable_override(monkeypatch):
    monkeypatch.setenv(
        "CHATBOT_API_VERSION",
        "v2",
    )

    settings = Settings(_env_file=None)

    assert settings.api_version == "v2"


def test_allowed_origins_from_environment(monkeypatch):
    monkeypatch.setenv(
        "CHATBOT_ALLOWED_ORIGINS",
        '["http://localhost:5173","https://example.com"]',
    )

    settings = Settings(_env_file=None)

    assert settings.allowed_origins == [
        "http://localhost:5173",
        "https://example.com",
    ]
