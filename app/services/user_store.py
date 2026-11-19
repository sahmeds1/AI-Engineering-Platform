from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.auth import UserResponse


class UserStore:
    
    def list_users(self) -> list[UserResponse]:
        return [
            self.to_user_response(user)
            for user in self._users_by_id.values()
        ]
        
    def update_role(
            self,
            user_id: str,
            role: str,
        ) -> UserResponse|None:
        user = self._users_by_id.get(user_id)
        if  user is None:
            return None
        
        if role not in ["user", "admin"]:
            raise ValueError("Invalid role. Must be 'user' or 'admin'.")
        
        
        user["role"] = role
        return self.to_user_response(user)

    def __init__(self) -> None:
        self._users_by_email: dict[str, dict] = {}
        self._users_by_id: dict[str, dict] = {}

    def create_user(
        self,
        email: str,
        hashed_password: str,
    ) -> UserResponse:
        normalized_email = email.strip().lower()

        if normalized_email in self._users_by_email:
            raise ValueError("User already exists")

        user_id = str(uuid4())

        record = {
            "id": user_id,
            "email": normalized_email,
            "hashed_password": hashed_password,
            "role": "user",
            "created_at": datetime.now(timezone.utc),
        }

        self._users_by_email[normalized_email] = record
        self._users_by_id[user_id] = record

        return self.to_user_response(record)
    
    

    def get_by_email(self, email: str) -> dict | None:
        return self._users_by_email.get(email.strip().lower())

    def get_by_id(self, user_id: str) -> dict | None:
        return self._users_by_id.get(user_id)

    @staticmethod
    def to_user_response(record: dict) -> UserResponse:
        return UserResponse(
            id=record["id"],
            email=record["email"],
            role=record["role"],
            created_at=record["created_at"],
        )


user_store = UserStore()