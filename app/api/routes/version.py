
from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import VersionResponse

router = APIRouter(
    prefix="/version",
    tags=["Version"],
)


@router.get("", response_model=VersionResponse)
def get_version() -> VersionResponse:
    settings = get_settings()

    return VersionResponse(
        application=settings.app_name,
        version=settings.api_version,
    )
