from delivery_service.domain.orders.order_ids import OrderID, OrderLineID
from delivery_service.domain.products.product import ProductID
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.shared.vo.quantity import Quantity


class OrderLine(Entity[OrderLineID]):
    def __init__(
        self,
        entity_id: OrderLineID,
        *,
        order_id: OrderID,
        product_id: ProductID,
        title: str,
        price_per_item: Price,
        quantity: Quantity,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._order_id = order_id
        self._product_id = product_id

        self._title = title
        self._price_per_item = price_per_item
        self._quantity = quantity

    def add_quantity(self, quantity_to_add: Quantity) -> None:
        self._quantity += quantity_to_add

    def reduce_quantity(self, quantity_to_reduce: Quantity) -> None:
        self._quantity -= quantity_to_reduce

    @property
    def id(self) -> OrderLineID:
        return self.entity_id

    @property
    def product_reference(self) -> ProductID:
        return self._product_id

    @property
    def line_title(self) -> str:
        return self._title

    @property
    def total_quantity(self) -> Quantity:
        return self._quantity

    @property
    def unit_price(self) -> Price:
        return self._price_per_item

    @property
    def total_position_price(self) -> Price:
        return self._price_per_item * FixedDecimal(self._quantity.value)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"entity_id={self.entity_id!r}, "
            f"title={self._title!r}, "
            f"price_per_item={self._price_per_item!r}, "
            f"quantity={self._quantity!r}"
            ")"
        )

    def __str__(self) -> str:
        return f"{self._quantity}×{self._title} @ {self._price_per_item}"
