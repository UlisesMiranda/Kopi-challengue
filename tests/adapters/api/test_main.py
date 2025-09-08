import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from chatbot.adapters.api.main import app, get_chat_service
from chatbot.domain.models import Conversation, ChatMessage
from chatbot.domain.ports import ChatUseCase

client = TestClient(app)


@pytest.fixture(autouse=True)
def auto_clear_dependency_overrides():
    """
    Fixture that automatically clears FastAPI dependency overrides after each test.

    This ensures that tests are isolated and don't affect each other's dependency configurations.
    """
    yield  # Allow the test to execute
    app.dependency_overrides.clear()  # Clear overrides after the test


def test_chat_new_conversation_success():
    """
    Tests the successful creation of a new conversation via the /chat endpoint.
    """
    mock_service = MagicMock(spec=ChatUseCase)

    mock_conversation = Conversation(
        id="new-convo-123",
        topic="earth_shape",
        strategy="earth_flat",
        oppose_user=True,
        messages=[
            ChatMessage(role="user", message="The Earth is round"),
            ChatMessage(role="bot", message="I disagree, it's flat.")
        ]
    )
    mock_service.process_message.return_value = mock_conversation

    app.dependency_overrides[get_chat_service] = lambda: mock_service

    response = client.post(
        "/chat",
        json={"message": "The Earth is round"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["conversation_id"] == "new-convo-123"
    assert len(response_data["message"]) == 2

    mock_service.process_message.assert_called_once_with(
        message="The Earth is round",
        conversation_id=None
    )


def test_chat_conversation_not_found():
    """
    Tests the scenario where a conversation is not found when processing a message.
    """

    mock_service = MagicMock(spec=ChatUseCase)
    mock_service.process_message.side_effect = ValueError("Conversation not found")

    app.dependency_overrides[get_chat_service] = lambda: mock_service

    response = client.post(
        "/chat",
        json={"conversation_id": "invalid-id", "message": "Hello"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found"}

    mock_service.process_message.assert_called_once_with(
        message="Hello",
        conversation_id="invalid-id"
    )


def test_chat_invalid_payload():
    """
    Tests the handling of an invalid payload sent to the /chat endpoint.
    """
    response = client.post(
        "/chat",
        json={"conversation_id": "some-id"}
    )

    assert response.status_code == 422


def test_health_check():
    """
    Tests the health check endpoint to ensure it returns a healthy status.
    """
    response = client.get("/health")

    assert response.status_code == 200
    response_data = response.json()

    assert "status" in response_data
    assert "timestamp" in response_data
    assert response_data["status"] == "healthy"
