from abc import ABC, abstractmethod
from typing import Optional
from .models import Conversation, ChatMessage


class ConversationRepository(ABC):
    """Port for conversation persistence."""

    @abstractmethod
    def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Finds a conversation by its ID.

        Args:
            conversation_id (str): The ID of the conversation to find.

        Returns:
            Optional[Conversation]: The found conversation, or None if not found.
        """
        pass

    @abstractmethod
    def save(self, conversation: Conversation):
        """
        Saves a conversation.

        Args:
            conversation (Conversation): The conversation to save.
        """
        pass


class ChatUseCase(ABC):
    """Input port for handling a chat."""

    @abstractmethod
    def process_message(self, message: str, conversation_id: Optional[str] = None) -> Conversation:
        """Processes a user message and updates/creates a conversation."""
        pass


class GenerativeAIProvider(ABC):
    """Puerto para un proveedor de IA generativa."""

    @abstractmethod
    def get_debate_response(self, topic: str, position: str, history: list[ChatMessage]) -> str:
        """
        Generates a debate response based on a topic, a position, and the conversation history.

        Args:
            topic (str): The topic of the debate.
            position (str): The position taken in the debate.
            history (list[ChatMessage]): A list of previous chat messages in the conversation.

        Returns:
            str: The generated debate response.
        """
        pass

    @abstractmethod
    def classify_topic_and_stance(self, message: str) -> dict:
        """
        Classifies the user's topic and stance from a given message.

        Args:
            message (str): The message to classify.

        Returns:
            dict: A dictionary containing the classified topic and stance.
                  Example: {"topic": "climate change", "stance": "pro"}
        """
        pass
