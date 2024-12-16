from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass
from typing import Sequence

from application.common.persistence.view_models import ShopView
from entities.shop.models import Shop, ShopId
from entities.user.models import UserId


@dataclass(frozen=True)
class ShopGatewayFilters:
    is_active: bool | None = None


class ShopGateway(Protocol):
    @abstractmethod
    async def load_with_id(self, shop_id: ShopId) -> Shop | None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_identity(self, user_id: UserId) -> Shop | None:
        raise NotImplementedError

    @abstractmethod
    async def load_many(
        self, filters: ShopGatewayFilters | None = None
    ) -> Sequence[Shop]:
        raise NotImplementedError


class ShopReader(Protocol):
    @abstractmethod
    async def read_with_id(self, shop_id: int) -> ShopView | None:
        raise NotImplementedError
