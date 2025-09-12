import pytest
from unittest.mock import Mock
from chatbot.domain.models import Conversation, ChatMessage
from chatbot.domain.services import ChatService, MAX_CONVERSATION_MESSAGES, MAX_USER_MESSAGES


@pytest.fixture
def mock_repository():
    """
    Fixture that returns a mock repository object.
    """
    return Mock()


@pytest.fixture
def mock_ai_provider():
    """
    Fixture that returns a mock AI provider object.
    """
    return Mock()


@pytest.fixture
def chat_service(mock_repository, mock_ai_provider):
    """
    Fixture that returns a ChatService instance with mocked repository and AI provider.

    Args:
        mock_repository (Mock): A mock repository object.
        mock_ai_provider (Mock): A mock AI provider object.

    """
    return ChatService(repository=mock_repository, ai_provider=mock_ai_provider)


def test_process_message_stops_when_conversation_limit_is_reached(
        chat_service: ChatService,
        mock_repository: Mock,
        mock_ai_provider: Mock
):
    """
    Tests that the process_message method correctly handles the scenario
    where the conversation message limit is reached.

    Args:
        chat_service (ChatService): The ChatService instance under test.
        mock_repository (Mock): The mocked repository.
        mock_ai_provider (Mock): The mocked AI provider.
    """

    full_conversation = Conversation(id="full-convo-123", topic="testing", strategy="strategy")
    full_conversation.messages = [
        ChatMessage(role="user", message=f"msg {i}") for i in range(MAX_CONVERSATION_MESSAGES)
    ]

    mock_repository.find_by_id.return_value = full_conversation

    final_conversation = chat_service.process_message(
        message="One more message",
        conversation_id="full-convo-123"
    )

    assert len(final_conversation.messages) == MAX_CONVERSATION_MESSAGES + 2

    expected_response = f"You have reached the {MAX_USER_MESSAGES}-message limit for this conversation. Please start a new one to discuss another topic."
    assert final_conversation.messages[-1].role == "bot"
    assert final_conversation.messages[-1].message == expected_response

    mock_ai_provider.is_topic_change.assert_not_called()
    mock_ai_provider.get_debate_response.assert_not_called()

    mock_repository.save.assert_called_once_with(final_conversation)
