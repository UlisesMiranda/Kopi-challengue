import os
from typing import Optional

import redis
from chatbot.domain.models import Conversation
from chatbot.domain.ports import ConversationRepository


class RedisConversationRepository(ConversationRepository):
    """
    Implementation of the ConversationRepository using Redis for persistence.
    """

    def __init__(self):
        """
        Initializes the RedisConversationRepository.

        Connects to Redis using the URL provided in the REDIS_URL environment variable,
        defaulting to 'redis://localhost:6379' if not set.
        """
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.from_url(redis_url, decode_responses=True)
        print(f"Connecting to Redis at {redis_url}")

    def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Finds a conversation by its ID in Redis.

        Args:
            conversation_id (str): The ID of the conversation to find.

        Returns:
            Optional[Conversation]: The found Conversation object, or None if not found.
        """
        data = self.client.get(conversation_id)
        if data:
            return Conversation.model_validate_json(data)
        return None

    def save(self, conversation: Conversation):
        """
        Saves a conversation to Redis, serializing it to JSON.

        Args:
            conversation (Conversation): The Conversation object to save.
        """
        self.client.set(conversation.id, conversation.model_dump_json())
