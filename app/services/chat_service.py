
import asyncio
from uuid import uuid4

from app.core.config import get_settings
from app.core.exceptions import (
    ConversationNotFoundException,
    ExternalServiceTimeoutException,
)
from app.llm.base import BaseLLMProvider, LLMMessage
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)
from app.services.conversation_store import conversation_store


settings = get_settings()

external_service_semaphore = asyncio.Semaphore(
    settings.max_concurrent_external_requests
)


class ChatService:
    """Handles chatbot business logic using an injected LLM provider."""

    def __init__(self, provider: BaseLLMProvider) -> None:
        self._provider = provider

    async def send_message(
        self,
        request: ChatRequest,
        user_id: str,
    ) -> ChatResponse:
        settings = get_settings()

        conversation_id = request.conversation_id or str(uuid4())

        # Verify ownership before retrieving conversation history or
        # making an external LLM call.
        if not conversation_store.can_access(conversation_id, user_id):
            raise ConversationNotFoundException()

        previous_messages = conversation_store.get_messages(
            conversation_id,
            user_id,
        )

        # A new, accessible conversation has no stored messages yet.
        if previous_messages is None:
            previous_messages = []

        # Retain only the most recent configured number of messages.
        previous_messages = previous_messages[
            -settings.max_conversation_history:
        ]

        messages = [
            LLMMessage(
                role="system",
                content=(
                    "You are a helpful, accurate, and professional "
                    "AI assistant. If you do not know an answer, "
                    "say so clearly."
                ),
            )
        ]

        messages.extend(
            LLMMessage(
                role=message.role,
                content=message.content,
            )
            for message in previous_messages
        )

        messages.append(
            LLMMessage(
                role="user",
                content=request.message,
            )
        )

        # Limit concurrent external calls and enforce an overall timeout.
        try:
            async with external_service_semaphore:
                result = await asyncio.wait_for(
                    self._provider.generate(messages),
                    timeout=settings.llm_timeout_seconds,
                )
        except asyncio.TimeoutError:
            raise ExternalServiceTimeoutException() from None

        generated_response = result.content

        # Persist the exchange only after successful LLM generation.
        # add_messages rechecks ownership to protect against ownership races.
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
        messages = conversation_store.get_messages(
            conversation_id,
            user_id,
        )

        if messages is None:
            return None

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            total_messages=len(messages),
        )
