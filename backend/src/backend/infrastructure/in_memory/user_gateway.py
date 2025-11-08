import uuid
from typing import Any

from backend.application.interfaces import CreateUserViaTgDTO, UserGateway
from backend.application.vars import UserId


class InMemoryUserGateway(UserGateway):
    def __init__(self) -> None:
        self.users: dict[UserId, Any] = {}

    async def create_user_via_tg(self, dto: CreateUserViaTgDTO) -> None:
        self.users[dto.user_id] = {
            "tg_id": dto.tg_id,
            "full_name": dto.full_name,
        }

    def next_id(self) -> UserId:
        return UserId(uuid.uuid4())
