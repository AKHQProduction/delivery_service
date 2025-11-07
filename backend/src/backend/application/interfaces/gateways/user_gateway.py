from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.vars import UserId


@dataclass(frozen=True)
class CreateUserViaTgDTO:
    user_id: UserId
    tg_id: int
    full_name: str


class UserGateway(Protocol):
    @abstractmethod
    async def create_user_via_tg(self, data: CreateUserViaTgDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> UserId:
        raise NotImplementedError
