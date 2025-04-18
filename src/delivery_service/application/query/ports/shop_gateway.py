from abc import abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from delivery_service.domain.shared.shop_id import ShopID


@dataclass(frozen=True)
class ShopReadModel:
    shop_id: ShopID
    regular_days_off: list[int]
    irregular_days_off: list[date]


class ShopGateway(Protocol):
    @abstractmethod
    async def read_with_id(self, shop_id: ShopID) -> ShopReadModel | None:
        raise NotImplementedError
