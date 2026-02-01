from dataclasses import dataclass

from backend.application.vars import CategoryId, ShopId


@dataclass
class Category:
    category_id: CategoryId
    shop_id: ShopId
    name: str


@dataclass(frozen=True)
class CreateCategoryDTO:
    category_id: CategoryId
    shop_id: ShopId
    name: str


@dataclass(frozen=True)
class CategoryReadModel:
    category_id: CategoryId
    name: str


@dataclass(frozen=True)
class GetCategoriesFilters:
    shop_id: ShopId | None = None
    name: str | None = None
