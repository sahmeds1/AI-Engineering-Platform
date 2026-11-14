
import logging

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.schemas.health import HealthResponse, VersionResponse


settings = get_settings()

configure_logging(settings.log_level)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    debug=settings.debug,
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    logger.info("Health check requested")

    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        environment=settings.environment,
    )

@app.get("/version", response_model=VersionResponse)
def get_application_version() -> VersionResponse:
    logger.info("Application version Requested")
    
    return VersionResponse(
        application=settings.app_name,
        version=settings.api_version,
    )
