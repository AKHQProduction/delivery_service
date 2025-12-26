from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.interfaces.gateways import Pagination
from backend.application.vars import ProductCategory, ProductId, ShopId


@dataclass
class Product:  # Like entity
    product_id: ProductId
    shop_id: ShopId
    name: str
    price: int
    category: ProductCategory


@dataclass(frozen=True)
class CreateProductDTO:
    product_id: ProductId
    shop_id: ShopId
    name: str
    price: int
    category: ProductCategory


@dataclass(frozen=True)
class ProductReadModel:
    product_id: ProductId
    name: str
    price: int
    category: ProductCategory


@dataclass(frozen=True)
class GetProductsFilters:
    shop_id: ShopId | None = None
    name: str | None = None


class ProductGateway(Protocol):
    @abstractmethod
    async def create_product(self, dto: CreateProductDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, product_id: ProductId) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    async def load_many(self, product_ids: list[ProductId]) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, updated_product: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, product_id: ProductId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read(
        self, product_id: ProductId, shop_id: ShopId
    ) -> ProductReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_all(
        self, filters: GetProductsFilters, pagination: Pagination
    ) -> list[ProductReadModel]:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> ProductId:
        raise NotImplementedError
