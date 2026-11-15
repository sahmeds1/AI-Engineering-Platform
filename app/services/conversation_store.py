
from app.schemas.chat import ChatMessage


class ConversationStore:
    """Temporary in-memory conversation storage."""

    def __init__(self) -> None:
        self._conversations: dict[str, list[ChatMessage]] = {}

    def add_message(
        self,
        conversation_id: str,
        message: ChatMessage,
    ) -> None:
        """Add a message to a conversation."""

        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        self._conversations[conversation_id].append(message)

    def get_messages(
        self,
        conversation_id: str,
    ) -> list[ChatMessage] | None:
        """Retrieve messages for a conversation."""

        messages = self._conversations.get(conversation_id)

        if messages is None:
            return None

        return list(messages)


# One shared store instance for this application process.
conversation_store = ConversationStore()
