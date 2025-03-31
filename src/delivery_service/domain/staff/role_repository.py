from abc import abstractmethod
from typing import Protocol, Sequence

from delivery_service.domain.staff.staff_role import Role, StaffRole


class RoleRepository(Protocol):
    @abstractmethod
    async def load_with_names(self, names: list[Role]) -> Sequence[StaffRole]:
        raise NotImplementedError
