from abc import abstractmethod
from datetime import date
from typing import Protocol

from delivery_service.domain.orders.order import Order
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.address import Coordinates


class OrderListCollector(Protocol):
    @abstractmethod
    async def collect_orders_by_proximity(
        self,
        shop_id: ShopID,
        shop_coordinates: Coordinates,
        delivery_date: date,
    ) -> list[Order]:
        pass
