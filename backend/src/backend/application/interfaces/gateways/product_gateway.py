from dataclasses import dataclass
from decimal import Decimal

from backend.application.vars import CategoryId, ProductId, ShopId


@dataclass
class Product:
    product_id: ProductId
    shop_id: ShopId
    name: str
    price: Decimal
    category_id: CategoryId | None


@dataclass(frozen=True)
class CreateProductDTO:
    product_id: ProductId
    shop_id: ShopId
    name: str
    price: Decimal
    category_id: CategoryId | None


@dataclass(frozen=True)
class ProductReadModel:
    product_id: ProductId
    name: str
    price: int
    category_id: CategoryId | None
    category_name: str | None


@dataclass(frozen=True)
class GetProductsFilters:
    shop_id: ShopId | None = None
    name: str | None = None
