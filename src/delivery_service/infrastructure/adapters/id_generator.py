from uuid import UUID

from uuid_extensions import uuid7

from delivery_service.application.ports.id_generator import (
    IDGenerator,
)
from delivery_service.domain.orders.order_ids import OrderID
from delivery_service.domain.products.product import ProductID
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID


class IDGeneratorImpl(IDGenerator):
    def generate_user_id(self) -> UserID:
        return UserID(UUID(str(uuid7())))

    def generate_shop_id(self) -> ShopID:
        return ShopID(UUID(str(uuid7())))

    def generate_product_id(self) -> ProductID:
        return ProductID(UUID(str(uuid7())))

    def generate_order_id(self) -> OrderID:
        return OrderID(UUID(str(uuid7())))
