from abc import abstractmethod
from asyncio import Protocol

from entities.employee.models import Employee, EmployeeId
from entities.user.models import UserId


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
