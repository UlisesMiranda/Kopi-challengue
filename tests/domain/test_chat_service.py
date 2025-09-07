import pytest
from unittest.mock import Mock, MagicMock

from chatbot.domain.models import ChatMessage, Conversation
# ¡Importamos los nuevos puertos que vamos a mockear!
from chatbot.domain.ports import ConversationRepository, GenerativeAIProvider
from chatbot.domain.services import ChatService


@pytest.fixture
def mock_repository() -> Mock:
    """
    Fixture to provide a mocked ConversationRepository.
    Returns:
        Mock: A MagicMock instance for ConversationRepository.
    """
    return MagicMock(spec=ConversationRepository)


@pytest.fixture
def mock_ai_provider() -> Mock:
    """
    Fixture to provide a mocked GenerativeAIProvider.
    Returns:
        Mock: A MagicMock instance for GenerativeAIProvider.
    """
    return MagicMock(spec=GenerativeAIProvider)


@pytest.fixture
def chat_service(mock_repository: Mock, mock_ai_provider: Mock) -> ChatService:
    """
    Fixture to provide a ChatService instance with mocked dependencies.
    Args:
        mock_repository (Mock): The mocked ConversationRepository.
        mock_ai_provider (Mock): The mocked GenerativeAIProvider.
    Returns:
        ChatService: An instance of ChatService.
    """
    return ChatService(repository=mock_repository, ai_provider=mock_ai_provider)


def test_process_message_for_new_conversation(
    chat_service: ChatService, mock_repository: Mock, mock_ai_provider: Mock
):
    """
    Tests the process_message method when a new conversation is initiated.
    Verifies that a new conversation is created, topic and stance are classified,
    a debate response is generated, and the conversation is saved.
    Args:
        chat_service (ChatService): The ChatService instance under test.
        mock_repository (Mock): The mocked ConversationRepository.
        mock_ai_provider (Mock): The mocked GenerativeAIProvider.
    """
    user_message = "I think the moon landing was real."

    mock_ai_provider.classify_topic_and_stance.return_value = {
        "topic": "Moon Landing",
        "stance": "pro-moon-landing"
    }
    mock_ai_provider.get_debate_response.return_value = "That's a naive perspective."
    mock_repository.find_by_id.return_value = None

    result_conversation = chat_service.process_message(message=user_message)

    mock_ai_provider.classify_topic_and_stance.assert_called_once_with(user_message)

    mock_ai_provider.get_debate_response.assert_called_once()

    mock_repository.save.assert_called_once_with(result_conversation)

    assert result_conversation.topic == "Moon Landing"
    assert len(result_conversation.messages) == 2
    assert result_conversation.messages[1].message == "That's a naive perspective."


def test_process_message_for_existing_conversation(
    chat_service: ChatService, mock_repository: Mock, mock_ai_provider: Mock
):
    """
    Tests the process_message method for an existing conversation.
    Verifies that the existing conversation is loaded, the user message is added,
    a debate response is generated, and the updated conversation is saved.
    Args:
        chat_service (ChatService): The ChatService instance under test.
        mock_repository (Mock): The mocked ConversationRepository.
        mock_ai_provider (Mock): The mocked GenerativeAIProvider.
    """
    conversation_id = "existing-id-123"
    user_message = "But the evidence is overwhelming!"

    existing_conversation = Conversation(
        id=conversation_id,
        topic="Moon Landing",
        strategy="Opposing the user's stance on Moon Landing",
        oppose_user=True,
        messages=[ChatMessage(role="user", message="Initial message")]
    )
    mock_repository.find_by_id.return_value = existing_conversation
    mock_ai_provider.get_debate_response.return_value = "Evidence can be fabricated."

    result_conversation = chat_service.process_message(
        message=user_message, conversation_id=conversation_id
    )

    mock_repository.find_by_id.assert_called_once_with(conversation_id)

    mock_ai_provider.classify_topic_and_stance.assert_not_called()

    mock_ai_provider.get_debate_response.assert_called_once()

    mock_repository.save.assert_called_once_with(result_conversation)

    assert len(result_conversation.messages) == 3
    assert result_conversation.messages[2].message == "Evidence can be fabricated."


def test_process_message_for_invalid_conversation_id(
    chat_service: ChatService, mock_repository: Mock, mock_ai_provider: Mock
):
    """
    Tests the process_message method when an invalid conversation ID is provided.
    Verifies that a ValueError is raised and no AI or repository operations are performed.
    Args:
        chat_service (ChatService): The ChatService instance under test.
        mock_repository (Mock): The mocked ConversationRepository.
        mock_ai_provider (Mock): The mocked GenerativeAIProvider.
    """
    mock_repository.find_by_id.return_value = None

    with pytest.raises(ValueError, match="Conversation not found"):
        chat_service.process_message(message="test", conversation_id="invalid-id")

    mock_ai_provider.classify_topic_and_stance.assert_not_called()
    mock_ai_provider.get_debate_response.assert_not_called()
    mock_repository.save.assert_not_called()
