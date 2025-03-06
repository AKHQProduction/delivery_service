from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass
from typing import Sequence

from application.common.persistence.view_models import EmployeeView
from entities.employee.models import Employee, EmployeeId
from entities.user.models import UserId


class EmployeeGateway(Protocol):
    @abstractmethod
    async def is_exist(self, user_id: UserId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_with_identity(self, user_id: UserId) -> Employee | None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_id(self, employee_id: EmployeeId) -> Employee | None:
        raise NotImplementedError


@dataclass(frozen=True)
class EmployeeReaderFilters:
    shop_id: int | None = None


class EmployeeReader(Protocol):
    @abstractmethod
    async def read_many(
        self, filters: EmployeeReaderFilters | None = None
    ) -> Sequence[EmployeeView]:
        raise NotImplementedError

    @abstractmethod
    async def read_with_id(self, employee_id: int) -> EmployeeView | None:
        raise NotImplementedError
