
import asyncio
from uuid import uuid4

from app.core.config import get_settings
from app.core.exceptions import (
    ConversationNotFoundException,
    ExternalServiceTimeoutException,
)

settings = get_settings()

external_service_semaphore = asyncio.Semaphore(
    settings.max_concurrent_external_requests
)
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)
from app.services.conversation_store import conversation_store


class ChatService:
    """Handles chatbot business logic."""

    async def send_message(
        self,
        request: ChatRequest,
        user_id: str,
    ) -> ChatResponse:
        # Step 1: Generate conversation ID if one is not provided.
        conversation_id = request.conversation_id or str(uuid4())

        if not conversation_store.can_access(conversation_id, user_id):
            raise ConversationNotFoundException()

        # Step 2: Generate chatbot response.
        generated_response = await self.generate_response(
            request.message
        )

        # Step 3: Store the exchange only if the caller owns the conversation.
        stored = conversation_store.add_messages(
            conversation_id,
            user_id,
            [
                ChatMessage(
                    role="user",
                    content=request.message,
                ),
                ChatMessage(
                    role="assistant",
                    content=generated_response,
                ),
            ],
        )
        if not stored:
            raise ConversationNotFoundException()

        # Step 5: Return API response.
        return ChatResponse(
            conversation_id=conversation_id,
            message=request.message,
            response=generated_response,
        )

    def get_conversation_history(
        self,
        conversation_id: str,
        user_id: str,
    ) -> ConversationHistoryResponse | None:

        # Step 1: Retrieve conversation messages.
        messages = conversation_store.get_messages(
            conversation_id,
            user_id,
        )

        # Step 2: Return None if conversation does not exist.
        if messages is None:
            return None

        # Step 3: Build conversation history response.
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            total_messages=len(messages),
        )

    async def generate_response(self, message: str) -> str:
        settings = get_settings()

        try:
            result = await asyncio.wait_for(
                self._simulate_external_service(message),
                timeout=settings.external_service_timeout_seconds,
            )

            return result

        except asyncio.TimeoutError as exc:
            raise ExternalServiceTimeoutException() from exc

    async def _simulate_external_service(
        self,
        message: str,
    ) -> str:
        # Simulate network I/O without blocking the event loop.
        await asyncio.sleep(1)

        return (
            f"Async chatbot response: "
            f"I received your message: {message}"
        )   


# Create a reusable service instance.
chat_service = ChatService()
