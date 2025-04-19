from datetime import date
from enum import Enum

from delivery_service.domain.orders.order_id import OrderID
from delivery_service.domain.orders.order_line import OrderLine
from delivery_service.domain.products.product import ProductID
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.shared.vo.quantity import Quantity


class DeliveryPreference(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"


class Order(Entity[OrderID]):
    def __init__(
        self,
        entity_id: OrderID,
        *,
        shop_id: ShopID,
        customer_id: UserID,
        delivery_preference: DeliveryPreference,
        order_lines: list[OrderLine],
        delivery_date: date,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._shop_id = shop_id
        self._customer_id = customer_id

        self._delivery_preference = delivery_preference
        self._order_lines = order_lines

        self._delivery_date = delivery_date

    def add_line(
        self,
        product_id: ProductID,
        title: str,
        price_per_item: FixedDecimal,
        quantity: int,
    ):
        for line in self._order_lines:
            if line.id == product_id and line.unit_price == Price(
                price_per_item
            ):
                return line.add_quantity(Quantity(quantity))

        new_line = OrderLine(
            entity_id=product_id,
            order_id=self.id,
            title=title,
            price_per_item=Price(price_per_item),
            quantity=Quantity(quantity),
        )

        return self._order_lines.append(new_line)

    def remove_positon(self, line_id: ProductID) -> None:
        for line in self._order_lines:
            if line.id == line_id:
                self._order_lines.remove(line)

    def reduce_quantity(
        self, quantity_to_reduce: Quantity, line_id: ProductID
    ) -> None:
        for line in self._order_lines:
            if line.id == line_id:
                line.reduce_quantity(quantity_to_reduce)

    @property
    def id(self) -> OrderID:
        return self.entity_id

    @property
    def order_lines(self) -> list[OrderLine]:
        return self._order_lines
