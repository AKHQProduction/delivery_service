from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.staff.staff_role import Role, StaffRole


class RoleRepository(Protocol):
    @abstractmethod
    async def load_with_name(self, name: Role) -> StaffRole | None:
        raise NotImplementedError
