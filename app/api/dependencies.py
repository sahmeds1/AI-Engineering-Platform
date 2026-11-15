
from app.services.chat_service import ChatService


def get_chat_service() -> ChatService:
    """Provide a ChatService instance."""
    return ChatService()
