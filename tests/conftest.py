
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.main import app
from app.schemas.auth import UserResponse


@pytest.fixture
def test_user() -> UserResponse:
    """Provide a simulated authenticated user for integration tests."""
    return UserResponse(
        id="test-user-id",
        email="test-user@example.com",
        role="user",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def authenticated_app(test_user):
    """Override authentication for tests that require a logged-in user."""
    previous_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_current_user] = lambda: test_user

    try:
        yield app
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = previous_override


@pytest.fixture
def authenticated_client(authenticated_app):
    """Provide a TestClient with the test user authenticated."""
    with TestClient(authenticated_app) as client:
        yield client
