from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.products.catalog import ShopCatalog
from delivery_service.domain.products.product import Product
from delivery_service.domain.shared.user_id import UserID


class ShopCatalogRepository(Protocol):
    @abstractmethod
    async def load_with_identity(
        self, identity_id: UserID
    ) -> ShopCatalog | None:
        raise NotImplementedError


class ProductRepository(Protocol):
    @abstractmethod
    def add(self, product: Product) -> None:
        raise NotImplementedError
