
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration."""

    # JWT authentication
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("development-only-change-this-secret"),
        min_length=32,
    )
    jwt_algorithm: str = "HS256"

    # External service configuration
    external_service_timeout_seconds: float = Field(
        default=5.0,
        gt=0,
        le=60,
    )

    # LLM provider configuration
    llm_provider: Literal[
        "openai",
        "bedrock",
        "azure_openai",
    ] = "openai"

    openai_api_key: SecretStr | None = None

    openai_model: str = "gpt-4.1-mini"

    llm_timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        le=300,
    )

    # Application configuration
    app_name: str = "Agentic AI Chatbot"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # API configuration
    api_version: str = "v1"

    request_timeout_seconds: int = Field(
        default=30,
        gt=0,
        le=300,
    )

    # Conversation configuration
    max_conversation_history: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    # CORS configuration
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHATBOT_",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
