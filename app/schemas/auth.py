from typing import Literal

from pydantic import BaseModel


class TokenClaims(BaseModel):
    sub: str
    role: Literal["user", "admin"]
    exp: int
