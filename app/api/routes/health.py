
from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        environment=settings.environment,
    )
