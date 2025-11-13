from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.vars import ShopRole, UserId


@dataclass(frozen=True)
class CurrentUserDTO:
    user_id: UserId
    role: ShopRole


class IdentityProvider(Protocol):
    @abstractmethod
    async def current_user_id(self) -> UserId | None:
        raise NotImplementedError

    @abstractmethod
    async def current_user(self) -> CurrentUserDTO:
        raise NotImplementedError
