
def test_unknown_conversation_returns_standard_error(authenticated_client):
    response = authenticated_client.get(
        "/api/v1/chat/unknown-conversation"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "CONVERSATION_NOT_FOUND"
    assert data["error"]["message"] == "Conversation not found."
    assert data["error"]["request_id"]


def test_invalid_chat_request_returns_standard_error(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/chat",
        json={"message": ""},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["request_id"]


def test_request_id_is_returned_in_response_header():
    from fastapi.testclient import TestClient

    from app.main import app

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
