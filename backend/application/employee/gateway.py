from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass

from application.common.input_data import Pagination
from entities.employee.models import Employee, EmployeeId
from entities.user.models import UserId


@dataclass(frozen=True)
class EmployeeFilters:
    shop_id: int


class EmployeeSaver(Protocol):
    @abstractmethod
    async def save(self, employee: Employee) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, employee_id: EmployeeId) -> None:
        raise NotImplementedError


class EmployeeReader(Protocol):
    @abstractmethod
    async def by_identity(self, user_id: UserId) -> Employee | None:
        raise NotImplementedError

    @abstractmethod
    async def all(
        self, filters: EmployeeFilters, pagination: Pagination
    ) -> list[Employee]:
        raise NotImplementedError

    @abstractmethod
    async def total(self, filters: EmployeeFilters) -> int:
        raise NotImplementedError
