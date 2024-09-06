from dataclasses import dataclass
from typing import NewType

UserId = NewType("UserId", int)


@dataclass
class User:
    user_id: UserId
    full_name: str
    username: str | None = None
    is_active: bool = True
