
from app.schemas.chat import ChatMessage


class ConversationStore:
    """Temporary in-memory conversation storage."""

    def __init__(self) -> None:
        self._conversations: dict[str, tuple[str, list[ChatMessage]]] = {}

    def add_messages(
        self,
        conversation_id: str,
        user_id: str,
        messages: list[ChatMessage],
    ) -> bool:
        """Append messages only when the conversation belongs to the user."""
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            self._conversations[conversation_id] = (user_id, list(messages))
            return True

        owner_id, stored_messages = conversation
        if owner_id != user_id:
            return False

        stored_messages.extend(messages)
        return True

    def can_access(self, conversation_id: str, user_id: str) -> bool:
        """Return whether a conversation is unowned or belongs to the user."""
        conversation = self._conversations.get(conversation_id)
        return conversation is None or conversation[0] == user_id

    def get_messages(
        self,
        conversation_id: str,
        user_id: str,
    ) -> list[ChatMessage] | None:
        """Retrieve messages only for the conversation owner."""

        conversation = self._conversations.get(conversation_id)

        if conversation is None or conversation[0] != user_id:
            return None

        return list(conversation[1])


# One shared store instance for this application process.
conversation_store = ConversationStore()
