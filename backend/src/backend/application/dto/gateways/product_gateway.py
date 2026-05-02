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
    category_id: CategoryId | None = None


@dataclass(frozen=True)
class ProductCategoryCountReadModel:
    category_id: CategoryId | None
    count: int


@dataclass(frozen=True)
class ProductSummaryReadModel:
    total_count: int
    category_counts: list[ProductCategoryCountReadModel]
