import operator
from datetime import date
from functools import reduce
from typing import cast

from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.orders.order_ids import OrderID, OrderLineID
from delivery_service.domain.orders.order_line import OrderLine
from delivery_service.domain.orders.value_object import TimeSlot
from delivery_service.domain.products.product import ProductID
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.shared.vo.quantity import Quantity


class Order(Entity[OrderID]):
    def __init__(
        self,
        entity_id: OrderID,
        *,
        shop_id: ShopID,
        customer_id: CustomerID,
        address_id: AddressID,
        phone_number: str,
        time_slot: TimeSlot,
        order_lines: list[OrderLine],
        delivery_date: date,
        note: str | None = None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._shop_id = shop_id
        self._customer_id = customer_id
        self._address_id = address_id
        self._phone_number = phone_number

        self._time_slot = time_slot
        self._delivery_date = delivery_date

        self._order_lines = order_lines
        self._note = note

    def add_line(
        self,
        product_id: ProductID,
        title: str,
        price_per_item: FixedDecimal,
        quantity: int,
    ) -> None:
        for line in self._order_lines:
            if (
                line.product_reference == product_id
                and line.unit_price == Price(price_per_item)
            ):
                return line.add_quantity(Quantity(quantity))

        new_line = OrderLine(
            entity_id=OrderLineID(cast(int, None)),
            order_id=self.id,
            product_id=product_id,
            title=title,
            price_per_item=Price(price_per_item),
            quantity=Quantity(quantity),
        )

        return self._order_lines.append(new_line)

    def remove_positon(self, line_id: OrderLineID) -> None:
        for line in self._order_lines:
            if line.id == line_id:
                self._order_lines.remove(line)

    def reduce_quantity(
        self, quantity_to_reduce: Quantity, line_id: OrderLineID
    ) -> None:
        for line in self._order_lines:
            if line.id == line_id:
                line.reduce_quantity(quantity_to_reduce)

    @property
    def id(self) -> OrderID:
        return self.entity_id

    @property
    def shop_reference(self) -> ShopID:
        return self._shop_id

    @property
    def address_reference(self) -> AddressID:
        return self._address_id

    @property
    def order_lines(self) -> list[OrderLine]:
        return self._order_lines

    @property
    def total_order_price(self) -> Price:
        zero = Price(FixedDecimal(0))

        return reduce(
            operator.add,
            (line.total_position_price for line in self._order_lines),
            zero,
        )

    @property
    def client_id(self) -> CustomerID:
        return self._customer_id

    @property
    def delivery_time_preference(self) -> TimeSlot:
        return self._time_slot

    @property
    def date(self) -> str:
        return self._delivery_date.strftime("%d.%m.%Y")

    @property
    def phone_number(self) -> str:
        return self._phone_number

    @property
    def note(self) -> str | None:
        return self._note
