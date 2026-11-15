
from fastapi.testclient import TestClient

import app.main as main_module
from app.core.config import Settings


client = TestClient(main_module.app)


def test_version_endpoint(monkeypatch):
    test_settings = Settings(
        _env_file=None,
        app_name="Test Chatbot",
        api_version="v99",
    )

    monkeypatch.setattr(
        main_module,
        "settings",
        test_settings,
    )

    response = client.get("/version")

    assert response.status_code == 200

    assert response.json() == {
        "application": "Test Chatbot",
        "version": "v99",
    }


def test_version_response_structure():
    response = client.get("/version")

    data = response.json()

    assert set(data.keys()) == {
        "application",
        "version",
    }


def test_version_response_content_types():
    response = client.get("/version")

    data = response.json()

    assert isinstance(data["application"], str)
    assert isinstance(data["version"], str)
