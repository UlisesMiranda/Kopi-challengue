import json

import pytest
from chatbot.adapters.storage.in_memory import InMemoryConversationRepository
from chatbot.bootstrap import get_chat_service
from chatbot.domain.services import ChatService
from fastapi.testclient import TestClient
from chatbot.adapters.api.main import app

client = TestClient(app)

MOCK_CLASSIFY_RESPONSE = {
    "topic": "vaccines",
    "stance": "pro-vaccine"
}
MOCK_DEBATE_RESPONSE_1 = "Have you considered the historical adverse reactions that caused public skepticism?"
MOCK_DEBATE_RESPONSE_2 = "Science isn't always clear, especially when studies are funded by pharmaceutical companies."

@pytest.fixture(autouse=True)
def override_dependencies():
    """
    Overrides the dependencies for testing purposes.
    """

    from chatbot.adapters.llm.openai_provider import OpenAIProvider
    repo = InMemoryConversationRepository()
    ai_provider = OpenAIProvider()
    test_service = ChatService(repository=repo, ai_provider=ai_provider)

    app.dependency_overrides[get_chat_service] = lambda: test_service

    yield

    app.dependency_overrides.clear()

def test_full_flow_new_and_continue_conversation(httpx_mock: object):
    """
    Tests the full conversation flow, including starting a new conversation and continuing an existing one.

    Args:
        httpx_mock (object): The httpx_mock fixture for mocking HTTP requests.
    """
    openai_url = "https://api.openai.com/v1/chat/completions"

    httpx_mock.add_response(
        url=openai_url,
        method="POST",
        json={"choices": [{"message": {"content": json.dumps(MOCK_CLASSIFY_RESPONSE)}}]}
    )
    httpx_mock.add_response(
        url=openai_url,
        method="POST",
        json={"choices": [{"message": {"content": MOCK_DEBATE_RESPONSE_1}}]}
    )

    initial_payload = {"message": "I believe vaccines are safe and effective."}
    response_1 = client.post("/chat", json=initial_payload)

    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert "conversation_id" in data_1
    assert data_1["message"][1]["role"] == "bot"
    assert data_1["message"][1]["message"] == MOCK_DEBATE_RESPONSE_1

    httpx_mock.add_response(
        url=openai_url,
        method="POST",
        json={"choices": [{"message": {"content": json.dumps({"is_topic_change": False})}}]}
    )

    httpx_mock.add_response(
        url=openai_url,
        method="POST",
        json={"choices": [{"message": {"content": MOCK_DEBATE_RESPONSE_2}}]}
    )

    conversation_id = data_1["conversation_id"]
    follow_up_payload = {
        "conversation_id": conversation_id,
        "message": "But the science is very clear on their benefits."
    }
    response_2 = client.post("/chat", json=follow_up_payload)

    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2["conversation_id"] == conversation_id
    assert len(data_2["message"]) == 4
    assert data_2["message"][3]["role"] == "bot"
    assert data_2["message"][3]["message"] == MOCK_DEBATE_RESPONSE_2

def test_health_check_integration():
    """
    Tests the health check endpoint to ensure the API is running.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
