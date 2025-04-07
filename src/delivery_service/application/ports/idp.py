from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.staff_role import RoleCollection


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserID:
        raise NotImplementedError

    @abstractmethod
    async def get_current_staff_roles(self) -> RoleCollection | None:
        raise NotImplementedError
