from typing import NewType
from uuid import UUID

from delivery_service.order_management.domain.order_line_collection import (
    OrderLineCollection,
)
from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.shop_id import ShopID

OrderID = NewType("OrderID", UUID)


class Order(Entity[OrderID]):
    def __init__(
        self,
        order_id: OrderID,
        *,
        shop_id: ShopID,
        order_lines: OrderLineCollection,
    ) -> None:
        super().__init__(entity_id=order_id)

        self._shop_id = shop_id
        self._order_lines = order_lines
