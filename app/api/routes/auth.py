from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.schemas.auth import TokenClaims


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/me", response_model=TokenClaims)
def get_my_profile(
    current_user: TokenClaims = Depends(get_current_user),
) -> TokenClaims:
    return current_user
