
from uuid import uuid4

from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)
from app.services.conversation_store import conversation_store


class ChatService:
    """Handles chatbot business logic."""

    def send_message(self, request: ChatRequest) -> ChatResponse:
        conversation_id = (
            request.conversation_id or str(uuid4())
        )

        generated_response = (
            "This is a demo chatbot response. "
            f"I received your message: {request.message}"
        )

        # Save the user's message.
        conversation_store.add_message(
            conversation_id,
            ChatMessage(
                role="user",
                content=request.message,
            ),
        )

        # Save the chatbot's response.
        conversation_store.add_message(
            conversation_id,
            ChatMessage(
                role="assistant",
                content=generated_response,
            ),
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message=request.message,
            response=generated_response,
        )

    def get_conversation_history(
        self,
        conversation_id: str,
    ) -> ConversationHistoryResponse | None:

        messages = conversation_store.get_messages(
            conversation_id
        )

        if messages is None:
            return None

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            total_messages=len(messages),
        )
