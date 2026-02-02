from dataclasses import dataclass

from backend.application.vars import CategoryId, ShopId


@dataclass(frozen=True)
class CategoryReadModel:
    category_id: CategoryId
    name: str


@dataclass(frozen=True)
class GetCategoriesFilters:
    shop_id: ShopId | None = None
    name: str | None = None
