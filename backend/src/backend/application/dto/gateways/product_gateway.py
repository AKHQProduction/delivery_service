from dataclasses import dataclass

from backend.application.vars import CategoryId, ProductId, ShopId


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
