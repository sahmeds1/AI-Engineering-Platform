
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


client = TestClient(app)
settings = get_settings()


def create_test_token(
    secret: str,
    expires_at: datetime,
) -> str:
    """
    Create a JWT token for authentication tests.

    The token uses a test user ID because these tests
    verify token validation failures before user lookup.
    """
    payload = {
        "sub": "test-user-id",
        "role": "user",
        "iat": datetime.now(timezone.utc) - timedelta(minutes=5),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        secret,
        algorithm=settings.jwt_algorithm,
    )


def test_expired_token_returns_401():
    expired_token = create_test_token(
        secret=settings.jwt_secret_key.get_secret_value(),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {expired_token}"
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"
    assert response.json()["error"]["request_id"]


def test_malformed_token_returns_401():
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer not-a-valid-jwt"
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"
    assert response.json()["error"]["request_id"]


def test_invalid_signature_returns_401():
    token_with_wrong_signature = create_test_token(
        secret="this-is-a-different-secret-key-for-testing-only",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token_with_wrong_signature}"
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"
    assert response.json()["error"]["request_id"]
