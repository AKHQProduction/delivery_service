from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass

from application.common.input_data import Pagination
from entities.shop.models import Shop, ShopId
from entities.user.models import UserId


@dataclass(frozen=True)
class ShopFilters:
    is_active: bool | None = None


class ShopReader(Protocol):
    @abstractmethod
    async def by_id(self, shop_id: ShopId) -> Shop | None:
        raise NotImplementedError

    @abstractmethod
    async def by_identity(self, user_id: UserId) -> Shop | None:
        raise NotImplementedError

    @abstractmethod
    async def all(
        self, filters: ShopFilters, pagination: Pagination
    ) -> list[Shop]:
        raise NotImplementedError

    @abstractmethod
    async def total(self, filters: ShopFilters) -> int:
        raise NotImplementedError


class ShopSaver(Protocol):
    @abstractmethod
    async def save(self, shop: Shop) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, shop_id: ShopId) -> None:
        raise NotImplementedError
