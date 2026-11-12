
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHATBOT_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Agentic AI Chatbot"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_version: str = "v1"

    request_timeout_seconds: int = Field(
        default=30,
        gt=0,
        le=300,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
