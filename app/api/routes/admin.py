
from fastapi import APIRouter, Depends

from app.api.dependencies import require_role
from app.schemas.auth import UserResponse
from app.services.user_store import user_store


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


@router.get(
    "/users",
    response_model=list[UserResponse],
)
def list_users(
    current_user: UserResponse = Depends(
        require_role("admin")
    ),
) -> list[UserResponse]:
    return user_store.list_users()
