from abc import abstractmethod
from typing import Protocol, Sequence

from delivery_service.domain.orders.order import Order
from delivery_service.domain.shared.shop_id import ShopID


class OrderRepository(Protocol):
    @abstractmethod
    def add(self, new_order: Order) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_many_with_shop_id(self, shop_id: ShopID) -> Sequence[Order]:
        raise NotImplementedError
