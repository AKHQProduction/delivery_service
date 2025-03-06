from abc import abstractmethod
from typing import Protocol

from delivery_service.identity.domain.user import User


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user(self) -> User:
        raise NotImplementedError
