from functools import lru_cache

from chatbot.adapters.llm.openai_provider import OpenAIProvider
from chatbot.domain.ports import ChatUseCase
from chatbot.domain.services import ChatService
from chatbot.adapters.storage.redis_repository import RedisConversationRepository


@lru_cache(maxsize=None)
def get_chat_service() -> ChatUseCase:
    """
    Initializes and returns a ChatService instance.
    This function is cached to ensure a single instance of ChatService is used application-wide.
    """
    _repository = RedisConversationRepository()

    _ai_provider = OpenAIProvider(model="gpt-4o-mini")

    return ChatService(repository=_repository, ai_provider=_ai_provider)
