
from fastapi import APIRouter, Depends, Path, status

from app.api.dependencies import get_chat_service, get_current_user
from app.core.exceptions import ConversationNotFoundException
from app.schemas.auth import UserResponse
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def send_message(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ChatResponse:
    """Receive a user message and return a chatbot response."""
    return await service.send_message(request, current_user.id)



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
    current_user: UserResponse = Depends(get_current_user),
) -> ConversationHistoryResponse:
    history = service.get_conversation_history(
        conversation_id,
        current_user.id,
    )

    if history is None:
        raise ConversationNotFoundException()

    return history
