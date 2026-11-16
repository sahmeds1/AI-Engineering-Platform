
from fastapi import APIRouter, Depends, status
from app.core.exceptions import ConversationNotFoundException
from app.api.dependencies import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)

@router.get(
    "/{conversation_id}",
    response_model=ConversationHistoryResponse,
)
def get_conversation_history(
    conversation_id: str = Path(
        min_length=1,
        max_length=100,
    ),
    service: ChatService = Depends(get_chat_service),
) -> ConversationHistoryResponse:

    history = service.get_conversation_history(
        conversation_id
    )

    if history is None:
        raise ConversationNotFoundException()
    

async def send_message(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Receive a user message and return a chatbot response."""

    return await service.send_message(request)
