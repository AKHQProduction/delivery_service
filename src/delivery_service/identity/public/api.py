from abc import abstractmethod
from typing import Protocol

from delivery_service.identity.public.identity_id import UserID


class IdentityAPI(Protocol):
    @abstractmethod
    async def get_current_identity(self) -> UserID:
        raise NotImplementedError
