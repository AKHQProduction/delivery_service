from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass
from datetime import datetime

from application.common.interfaces.filters import Pagination
from entities.shop.models import Shop, ShopId
from entities.user.models import UserId


@dataclass(frozen=True)
class ShopFilters:
    is_active: bool | None = None


class OldShopGateway(Protocol):
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


@dataclass(frozen=True)
class ShopInfo:
    title: str
    delivery_distance: int
    regular_days_off: list[int]
    special_days_off: list[datetime]


class ShopReader(Protocol):
    @abstractmethod
    async def get_by_id(self, shop_id: ShopId) -> ShopInfo | None:
        raise NotImplementedError
