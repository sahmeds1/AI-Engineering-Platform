
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_version_endpoint():
    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "Agentic AI Chatbot"
    assert data["version"] == "v1"


def test_version_response_structure():
    response = client.get("/version")

    data = response.json()

    assert set(data.keys()) == {"application", "version"}
