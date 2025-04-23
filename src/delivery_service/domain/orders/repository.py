from abc import abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Protocol, Sequence

from delivery_service.domain.orders.order import Order
from delivery_service.domain.orders.order_ids import OrderID
from delivery_service.domain.shared.shop_id import ShopID


@dataclass(frozen=True)
class OrderRepositoryFilters:
    shop_id: ShopID | None = None
    delivery_date: date | None = None


class OrderRepository(Protocol):
    @abstractmethod
    def add(self, new_order: Order) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_many(
        self, filters: OrderRepositoryFilters | None = None
    ) -> Sequence[Order]:
        raise NotImplementedError

    @abstractmethod
    async def load_with_id(self, order_id: OrderID) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, order: Order) -> None:
        raise NotImplementedError
