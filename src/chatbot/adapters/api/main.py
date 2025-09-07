from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends

from chatbot.bootstrap import get_chat_service  # Inyección de dependencias
from chatbot.domain.ports import ChatUseCase
from .models import ChatRequest, ChatResponse

app = FastAPI(title="Kopi-challenge API", version="1.0.0")


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatUseCase = Depends(get_chat_service)
):
    """
    Processes a chat message and returns the conversation.

    Args:
        request (ChatRequest): The request body containing the message and optional conversation ID.
        chat_service (ChatUseCase): The chat service dependency.

    Returns:
        ChatResponse: The response containing the conversation ID and messages.
    """
    try:
        conversation = chat_service.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )
        return ChatResponse(
            conversation_id=conversation.id,
            message=conversation.messages
        )
    except ValueError as e:
        if "Conversation not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@app.get("/health")
async def health_check():
    """
    Performs a health check on the API.

    Returns:
        dict: A dictionary indicating the status and current timestamp.
    """
    return {"status": "healthy", "timestamp": datetime.utcnow()}
