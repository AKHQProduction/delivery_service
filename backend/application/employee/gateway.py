from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass
from typing import Iterable

from application.common.interfaces.filters import Pagination
from application.employee.output_data import EmployeeCard
from entities.common.entity import OIDType
from entities.employee.models import Employee, EmployeeId
from entities.user.models import UserId


@dataclass(frozen=True)
class EmployeeFilters:
    shop_id: int | None = None


class EmployeeGateway(Protocol):
    @abstractmethod
    async def save(self, employee: Employee) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_exist(self, user_id: UserId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, employee_id: EmployeeId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def by_identity(self, user_id: OIDType) -> Employee | None:
        raise NotImplementedError

    @abstractmethod
    async def by_id(self, employee_id: EmployeeId) -> Employee | None:
        raise NotImplementedError


class EmployeeReader(Protocol):
    @abstractmethod
    async def all_cards(
        self, filters: EmployeeFilters, pagination: Pagination
    ) -> Iterable[EmployeeCard]:
        raise NotImplementedError

    @abstractmethod
    async def card_by_id(self, employee_id: EmployeeId) -> EmployeeCard | None:
        raise NotImplementedError

    @abstractmethod
    async def total(self, filters: EmployeeFilters) -> int:
        raise NotImplementedError
