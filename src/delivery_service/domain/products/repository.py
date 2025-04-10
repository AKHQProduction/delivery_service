from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.products.product import Product, ProductID
from delivery_service.domain.shared.shop_id import ShopID


class ProductRepository(Protocol):
    @abstractmethod
    def add(self, product: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, title: str, shop_id: ShopID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_with_id(self, product_id: ProductID) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, product: Product) -> None:
        raise NotImplementedError
