
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Incoming request from the chatbot client."""

    message: str = Field(
        min_length=1,
        max_length=4000,
        description="Message sent by the user",
    )

    conversation_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Existing conversation identifier",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty or whitespace")

        return value


class ChatResponse(BaseModel):
    """Response returned by the chatbot API."""

    conversation_id: str

    message: str

    response: str

    status: Literal["completed"] = "completed"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ChatMessage(BaseModel):
    """Represents one message in a conversation."""

    role: Literal["user", "assistant"]

    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ConversationHistoryResponse(BaseModel):
    """Represents the complete conversation history."""

    conversation_id: str

    messages: list[ChatMessage]

    total_messages: int
