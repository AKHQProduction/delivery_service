from uuid import UUID

from uuid_extensions import uuid7

from delivery_service.application.ports.id_generator import (
    IDGenerator,
)
from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.customers.phone_number_id import PhoneNumberID
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

    def generate_address_id(self) -> AddressID:
        return AddressID(UUID(str(uuid7())))

    def generate_phone_number_id(self) -> PhoneNumberID:
        return PhoneNumberID(UUID(str(uuid7())))

    def generate_customer_id(self) -> CustomerID:
        return CustomerID(UUID(str(uuid7())))
