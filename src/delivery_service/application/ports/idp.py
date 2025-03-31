from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.user_id import UserID


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserID:
        raise NotImplementedError
