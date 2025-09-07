from src.chatbot.adapters.storage.in_memory import InMemoryConversationRepository
from src.chatbot.domain.models import Conversation


def test_save_and_find_by_id_success():
    """
    Tests that a conversation can be successfully saved and retrieved by its ID.
    """
    repo = InMemoryConversationRepository()
    conversation = Conversation(
        id="test-id-1",
        topic="test",
        strategy="test_strat"
    )

    repo.save(conversation)
    retrieved_conversation = repo.find_by_id("test-id-1")

    assert retrieved_conversation is not None
    assert retrieved_conversation.id == "test-id-1"
    assert retrieved_conversation.topic == "test"
    assert retrieved_conversation == conversation


def test_find_by_id_not_found():
    """
    Tests that `find_by_id` returns None when a conversation with the given ID does not exist.
    """
    repo = InMemoryConversationRepository()

    result = repo.find_by_id("non-existent-id")

    assert result is None


def test_save_updates_existing_conversation():
    """
    Tests that saving a conversation with an existing ID updates the existing conversation.
    """
    repo = InMemoryConversationRepository()
    convo_v1 = Conversation(id="update-test", topic="v1", strategy="v1")
    repo.save(convo_v1)

    convo_v2 = Conversation(id="update-test", topic="v2", strategy="v2")

    repo.save(convo_v2)
    retrieved_conversation = repo.find_by_id("update-test")

    assert retrieved_conversation is not None
    assert retrieved_conversation.topic == "v2"
    assert retrieved_conversation != convo_v1
