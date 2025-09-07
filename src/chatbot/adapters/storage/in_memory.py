from typing import Dict, Optional

from chatbot.domain.models import Conversation
from chatbot.domain.ports import ConversationRepository


class InMemoryConversationRepository(ConversationRepository):
    """In-memory implementation of the conversation repository."""

    def __init__(self):
        """
        Initializes the InMemoryConversationRepository.

        This constructor sets up an empty dictionary to store conversations in memory.
        """
        self._conversations: Dict[str, Conversation] = {}

    def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Finds a conversation by its ID.

        Args:
            conversation_id (str): The unique identifier of the conversation.
        Returns:
            Optional[Conversation]: The conversation object if found, otherwise None."""
        return self._conversations.get(conversation_id)

    def save(self, conversation: Conversation):
        """
        Saves a conversation.

        If a conversation with the same ID already exists, it will be updated.
        Otherwise, a new conversation will be added.

        Args:
            conversation (Conversation): The conversation object to be saved.
        """
        self._conversations[conversation.id] = conversation
