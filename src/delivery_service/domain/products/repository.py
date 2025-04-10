from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.products.product import Product
from delivery_service.domain.shared.shop_id import ShopID


class ProductRepository(Protocol):
    @abstractmethod
    def add(self, product: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, title: str, shop_id: ShopID) -> bool:
        raise NotImplementedError
