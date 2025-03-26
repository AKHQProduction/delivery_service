from abc import abstractmethod
from typing import Protocol

from delivery_service.identity.public.identity_id import UserID
from delivery_service.products_management.domain.catalog import ShopCatalog
from delivery_service.products_management.domain.product import Product


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
