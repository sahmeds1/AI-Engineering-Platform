
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
