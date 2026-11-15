
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
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
