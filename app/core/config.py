
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DEVELOPMENT_JWT_SECRET = "development-only-change-this-secret"


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
    
    """Centralized application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHATBOT_",
        case_sensitive=False,
        extra="ignore",
    )

    jwt_secret_key: SecretStr = Field(
        default=SecretStr(DEFAULT_DEVELOPMENT_JWT_SECRET),
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        le=1440,
    )
    max_concurrent_external_requests: int = Field(
        default=3,
        gt=0,
        le=100,
    )
    external_service_timeout_seconds: float = Field(
        default=5.0,
        gt=0,
        le=60,
    )
    openai_api_key: SecretStr | None = None
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
    @model_validator(mode="after")
    def validate_production_jwt_secret(self) -> "Settings":
        secret = self.jwt_secret_key.get_secret_value()
        if self.environment.lower() != "development" and (
            secret == DEFAULT_DEVELOPMENT_JWT_SECRET
            or secret.lower().startswith(("replace-with-", "change-this-"))
        ):
            raise ValueError(
                "A deployment-specific CHATBOT_JWT_SECRET_KEY is required "
                "outside development."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
