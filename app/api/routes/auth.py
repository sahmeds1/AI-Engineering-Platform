from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import auth_service
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.schemas.auth import TokenClaims


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest) -> UserResponse:
    return auth_service.register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(request: LoginRequest) -> TokenResponse:
    return auth_service.login(
        email=str(request.email),
        password=request.password,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    return current_user
@router.get("/me", response_model=TokenClaims)
def get_my_profile(
    current_user: TokenClaims = Depends(get_current_user),
) -> TokenClaims:
    return current_user
