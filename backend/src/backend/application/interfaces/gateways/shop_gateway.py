from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

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
