from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.orders.order_id import OrderID
from delivery_service.domain.products.product import ProductID
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID


class IDGenerator(Protocol):
    @abstractmethod
    def generate_user_id(self) -> UserID:
        raise NotImplementedError

    @abstractmethod
    def generate_shop_id(self) -> ShopID:
        raise NotImplementedError

    @abstractmethod
    def generate_product_id(self) -> ProductID:
        raise NotImplementedError

    @abstractmethod
    def generate_order_id(self) -> OrderID:
        raise NotImplementedError
