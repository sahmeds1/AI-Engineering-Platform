
from functools import lru_cache


from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
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
    
    """Centralized application configuration."""
    openai_api_key: str | None = None
    openai_api_key: SecretStr | None = None
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
    max_conversation_history: int = Field(
            default=20,
            ge=1,
            le=100,
        )
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )    

@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
