from backend.application.vars import CategoryId, ShopId
from backend.infrastructure.persistence.tables import Category


def create_category(
    *,
    category_id: CategoryId,
    shop_id: ShopId,
    name: str,
) -> Category:
    return Category(id=category_id, shop_id=shop_id, name=name)


def update_category(category: Category, *, name: str) -> None:
    category.name = name
