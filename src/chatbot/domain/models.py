import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    Represents a single message within a chat conversation.

    Attributes:
        role (str): The role of the sender (e.g., "user", "bot").
        message (str): The content of the message.
    """
    role: str
    message: str


class Conversation(BaseModel):
    """
    Represents a complete conversation, including its metadata and messages.

    Attributes:
        id (str): A unique identifier for the conversation.
        topic (str): The main topic of the conversation.
        strategy (str): The conversational strategy employed.
        messages (List[ChatMessage]): A list of chat messages in chronological order.
        created_at (datetime): The timestamp when the conversation was created.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    strategy: str
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
