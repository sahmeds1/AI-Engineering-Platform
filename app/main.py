import logging

import time
from uuid import uuid4
from fastapi import FastAPI, Request    
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import ApplicationException
from app.schemas.errors import ErrorResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, chat, health, version
from app.core.config import get_settings
from app.core.logging_config import configure_logging

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from app.api.dependencies import close_llm_provider

settings = get_settings()

configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown resources."""

    try:
        yield
    finally:
        await close_llm_provider()

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router)
app.include_router(version.router)

# API v1 routers
app.include_router(
    auth.router,
    prefix=f"/api/{settings.api_version}",
)

app.include_router(
    chat.router,
    prefix=f"/api/{settings.api_version}",
)

app.include_router(
    admin.router,
    prefix=f"/api/{settings.api_version}",
)
@app.get("/")
def root():
    return {
        "message": "Welcome to Agentic AI Chatbot API"
    }


logger = logging.getLogger(__name__)


@app.exception_handler(ApplicationException)
async def application_exception_handler(
    request: Request,
    exc: ApplicationException,
):
    request_id = getattr(request.state, "request_id", "unknown")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error={
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
            }
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    request_id = getattr(request.state, "request_id", "unknown")

    # Do not expose arbitrary internal exception details.
    safe_messages = {
        400: ("BAD_REQUEST", "The request could not be processed."),
        401: ("UNAUTHORIZED", "Authentication is required."),
        403: ("FORBIDDEN", "You do not have permission to perform this action."),
        404: ("NOT_FOUND", "The requested resource was not found."),
        405: ("METHOD_NOT_ALLOWED", "The HTTP method is not allowed."),
    }

    code, message = safe_messages.get(
        exc.status_code,
        ("HTTP_ERROR", "The request could not be completed."),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error={
                "code": code,
                "message": message,
                "request_id": request_id,
            }
        ).model_dump(),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = getattr(request.state, "request_id", "unknown")

    # Do not return raw input values or internal validation details.
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error={
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid data.",
                "request_id": request_id,
            }
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(request.state, "request_id", "unknown")

    # Log only the exception type and correlation ID.
    # Do not log exception text, request bodies, or credentials.
    logger.error(

        "Unhandled application exception. type=%s request_id=%s",
        type(exc).__name__,
        request_id,
    )

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            }
        ).model_dump(),
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    route = request.scope.get("route")
    route_template = getattr(route, "path", "unmatched")

    logger.info(
        "HTTP request completed method=%s route=%s "
        "status=%s duration_ms=%.2f request_id=%s",
        request.method,
        route_template,
        response.status_code,
        duration_ms,
        request_id,
    )

    response.headers["X-Request-ID"] = request_id

    return response
