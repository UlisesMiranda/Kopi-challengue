from pydantic import BaseModel
from typing import List, Optional
from chatbot.domain.models import ChatMessage


class ChatRequest(BaseModel):
    """
    Represents a chat request from the user.

    Attributes:
        conversation_id (Optional[str]): The ID of the ongoing conversation. Defaults to None.
        message (str): The user's message.
    """
    conversation_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """
    Represents a chat response from the chatbot.

    Attributes:
        conversation_id (str): The ID of the conversation.
        message (List[ChatMessage]): A list of chat messages in the conversation.
    """
    conversation_id: str
    message: List[ChatMessage]
