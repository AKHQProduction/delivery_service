from dataclasses import dataclass

from backend.application.vars import UserId


@dataclass(frozen=True)
class CreateUserViaTgDTO:
    user_id: UserId
    tg_id: int
    full_name: str
