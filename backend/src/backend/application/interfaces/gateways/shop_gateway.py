from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.interfaces.gateways import Pagination
from backend.application.vars import ShopId, ShopRole, UserId


@dataclass(frozen=True)
class CreateNewShopDTO:
    shop_id: ShopId
    shop_name: str
    owner_name: str
    user_id: UserId


@dataclass  # Like entity
class ShopEmployee:
    user_id: UserId
    shop_id: ShopId
    full_name: str
    role: ShopRole


@dataclass(frozen=True)
class EmployeeReadModel:
    user_id: UserId
    full_name: str
    role: ShopRole


@dataclass(frozen=True)
class EmployeeFilters:
    shop_id: ShopId | None = None
    name: str | None = None


class ShopGateway(Protocol):
    @abstractmethod
    async def relate_to_shop(self, user_id: UserId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create_shop(self, dto: CreateNewShopDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_shop_employee(self, user_id: UserId) -> ShopEmployee | None:
        raise NotImplementedError

    @abstractmethod
    async def add_employee(self, employee: ShopEmployee) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_employee(self, updated_employee: ShopEmployee) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_employee(self, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> ShopId:
        raise NotImplementedError

    @abstractmethod
    async def read_employee(self, user_id: UserId) -> EmployeeReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_all_employees(
        self, filters: EmployeeFilters, pagination: Pagination
    ) -> list[EmployeeReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def get_shop_name(self, shop_id: ShopId) -> str | None:
        raise NotImplementedError
