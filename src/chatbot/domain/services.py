from typing import Optional

from .models import Conversation, ChatMessage
from .ports import ChatUseCase, ConversationRepository, GenerativeAIProvider

OPPOSING_STANCES = {
    "pro-moon-landing": "anti-moon-landing",
    "anti-moon-landing": "pro-moon-landing",
    "pro-vaccine": "anti-vaccine",
    "anti-vaccine": "pro-vaccine",
    "pro-climate-change": "anti-climate-change",
    "anti-climate-change": "pro-climate-change",
    "pro-flat-earth": "anti-flat-earth",
    "anti-flat-earth": "pro-flat-earth",
}


class ChatService(ChatUseCase):

    def __init__(self, repository: ConversationRepository, ai_provider: GenerativeAIProvider):
        """
        Initializes the ChatService with a conversation repository and an AI provider.

        Args:
            repository (ConversationRepository): The repository for managing conversations.
            ai_provider (GenerativeAIProvider): The AI provider for classifying topics and generating responses.
        """
        self._repository = repository
        self._ai_provider = ai_provider

    def process_message(self, message: str, conversation_id: Optional[str] = None) -> Conversation:
        """
        Processes a user message, either continuing an existing conversation or starting a new one.

        Args:
            message (str): The user's message.
            conversation_id (Optional[str]): The ID of an existing conversation, if applicable.

        Returns:
            Conversation: The updated or newly created conversation object.

        Raises:
            ValueError: If a conversation ID is provided but no matching conversation is found.
        """
        if conversation_id:
            conversation = self._repository.find_by_id(conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")

            if self._ai_provider.is_topic_change(message=message, original_topic=conversation.topic):
                conversation.messages.append(ChatMessage(role="user", message=message))
                bot_response = f"I'm sorry, but we are discussing '{conversation.topic}'. Let's stick to that topic."
                conversation.messages.append(ChatMessage(role="bot", message=bot_response))
                self._repository.save(conversation)
                return conversation

        else:
            topic_info = self._ai_provider.classify_topic_and_stance(message)
            user_stance = topic_info.get("stance", "unknown")

            bot_stance = OPPOSING_STANCES.get(user_stance, f"Opposing the user's stance on {topic_info['topic']}")

            conversation = Conversation(
                topic=topic_info["topic"],
                strategy=bot_stance
            )

        conversation.messages.append(ChatMessage(role="user", message=message))

        bot_response = self._ai_provider.get_debate_response(
            topic=conversation.topic,
            position=conversation.strategy,
            history=conversation.messages[-5:]
        )
        conversation.messages.append(ChatMessage(role="bot", message=bot_response))

        self._repository.save(conversation)
        return conversation
