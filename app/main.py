
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.schemas.health import HealthResponse


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["Authorization","Content-Type"]
)
