from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

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


class ProductGateway(Protocol):
    @abstractmethod
    async def create_product(self, dto: CreateProductDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, product_id: ProductId) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, updated_product: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> ProductId:
        raise NotImplementedError
