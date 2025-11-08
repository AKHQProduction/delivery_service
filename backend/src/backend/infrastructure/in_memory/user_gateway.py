import uuid
from typing import Any

from backend.application.interfaces import CreateUserViaTgDTO, UserGateway
from backend.application.vars import UserId


class InMemoryUserGateway(UserGateway):
    def __init__(self) -> None:
        self.users: dict[UserId, Any] = {}

    async def create_user_via_tg(self, data: CreateUserViaTgDTO) -> None:
        self.users[data.user_id] = {
            "tg_id": data.tg_id,
            "full_name": data.full_name,
        }

    def next_id(self) -> UserId:
        return UserId(uuid.uuid4())
