from abc import abstractmethod
from asyncio import Protocol

from entities.employee.models import Employee


class EmployeeSaver(Protocol):
    @abstractmethod
    async def save(self, employee: Employee) -> None:
        raise NotImplementedError
