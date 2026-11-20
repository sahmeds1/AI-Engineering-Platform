
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app


client = TestClient(app)


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.health.get_settings",
        lambda: Settings(_env_file=None),
    )
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "Agentic AI Chatbot"
    assert data["environment"] == "development"


def test_health_response_structure():
    response = client.get("/health")

    data = response.json()

    assert set(data.keys()) == {
        "status",
        "application",
        "environment",
    }
