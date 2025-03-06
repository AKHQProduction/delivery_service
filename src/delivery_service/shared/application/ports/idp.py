from abc import abstractmethod
from typing import Protocol

from delivery_service.shared.domain.identity_id import UserID


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserID:
        raise NotImplementedError
