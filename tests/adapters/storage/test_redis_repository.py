import pytest
from fakeredis import FakeStrictRedis

from src.chatbot.adapters.storage.redis_repository import RedisConversationRepository
from src.chatbot.domain.models import Conversation


@pytest.fixture
def mock_redis_repo(monkeypatch):
    """
    Fixture that provides a mocked RedisConversationRepository instance for testing.

    Args:
        monkeypatch: Pytest's monkeypatch fixture for modifying behavior during tests.
    """

    fake_redis_client = FakeStrictRedis(decode_responses=True)

    monkeypatch.setattr("redis.from_url", lambda *args, **kwargs: fake_redis_client)

    repo = RedisConversationRepository()

    yield repo

    fake_redis_client.flushall()


def test_save_and_find_by_id_success(mock_redis_repo: RedisConversationRepository):
    """
    Tests the successful saving and retrieval of a conversation by its ID.

    Args:
        mock_redis_repo: The mocked RedisConversationRepository instance.
    """

    conversation = Conversation(
        id="test-id-123",
        topic="redis-testing",
        strategy="pro-testing"
    )

    mock_redis_repo.save(conversation)

    retrieved_conversation = mock_redis_repo.find_by_id("test-id-123")

    assert retrieved_conversation is not None
    assert retrieved_conversation.id == "test-id-123"
    assert retrieved_conversation.topic == "redis-testing"
    assert retrieved_conversation.model_dump() == conversation.model_dump()


def test_find_by_id_not_found(mock_redis_repo: RedisConversationRepository):
    """
    Tests the scenario where a conversation is not found by its ID.

    Args:
        mock_redis_repo: The mocked RedisConversationRepository instance.
    """

    result = mock_redis_repo.find_by_id("non-existent-id")

    assert result is None


def test_save_updates_existing_conversation(mock_redis_repo: RedisConversationRepository):
    """
    Tests that saving a conversation with an existing ID updates the existing record.

    Args:
        mock_redis_repo: The mocked RedisConversationRepository instance.
    """

    convo_v1 = Conversation(id="update-test-id", topic="version1", strategy="strat_v1")
    mock_redis_repo.save(convo_v1)

    convo_v2 = Conversation(id="update-test-id", topic="version2", strategy="strat_v2")

    mock_redis_repo.save(convo_v2)
    retrieved_conversation = mock_redis_repo.find_by_id("update-test-id")

    assert retrieved_conversation is not None
    assert retrieved_conversation.topic == "version2"
    assert retrieved_conversation.model_dump() != convo_v1.model_dump()
    assert retrieved_conversation.model_dump() == convo_v2.model_dump()
