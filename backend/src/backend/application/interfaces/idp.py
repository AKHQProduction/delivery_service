from abc import abstractmethod
from typing import Protocol

from backend.application.vars import UserId


class IdentityProvider(Protocol):
    @abstractmethod
    async def current_user_id(self) -> UserId | None:
        raise NotImplementedError
