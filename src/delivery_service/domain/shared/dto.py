from dataclasses import dataclass

from delivery_service.domain.products.product import ProductID
from delivery_service.domain.shared.new_types import FixedDecimal


@dataclass
class OrderLineData:
    product_id: ProductID
    title: str
    price_per_item: FixedDecimal
    quantity: int
