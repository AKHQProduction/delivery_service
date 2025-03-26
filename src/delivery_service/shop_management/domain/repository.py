from abc import abstractmethod
from typing import Protocol

from delivery_service.identity.public.identity_id import UserID
from delivery_service.shared.domain.employee import Employee
from delivery_service.shop_management.domain.shop import Shop


class ShopRepository(Protocol):
    @abstractmethod
    def add(self, shop: Shop) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, identity_id: UserID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_with_identity(self, identity_id: UserID) -> Shop | None:
        raise NotImplementedError


class EmployeeRepository(Protocol):
    @abstractmethod
    def add(self, employee: Employee) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_id(self, employee_id: UserID) -> Employee | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, employee: Employee) -> None:
        raise NotImplementedError
