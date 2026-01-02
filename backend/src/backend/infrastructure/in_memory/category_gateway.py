from uuid import UUID

from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.category_gateway import (
    Category,
    CategoryGateway,
    CategoryReadModel,
    CreateCategoryDTO,
    GetCategoriesFilters,
)
from backend.application.vars import CategoryId, ShopId


class InMemoryCategoryGateway(CategoryGateway):
    def __init__(self) -> None:
        self.categories: dict[CategoryId, Category] = {}

    async def create_category(self, dto: CreateCategoryDTO) -> None:
        category = Category(
            category_id=dto.category_id,
            shop_id=dto.shop_id,
            name=dto.name,
        )
        self.categories.setdefault(dto.category_id, category)

    async def load(self, category_id: CategoryId) -> Category | None:
        return self.categories.get(category_id)

    async def update(self, updated_category: Category) -> None:
        if updated_category.category_id in self.categories:
            self.categories[updated_category.category_id] = updated_category

    async def delete(self, category_id: CategoryId) -> None:
        if category_id in self.categories:
            del self.categories[category_id]

    async def read_all(
        self, filters: GetCategoriesFilters, pagination: Pagination
    ) -> list[CategoryReadModel]:
        filtered = list(self.categories.values())

        if filters.shop_id:
            filtered = [c for c in filtered if c.shop_id == filters.shop_id]
        if filters.name:
            filtered = [
                c for c in filtered if filters.name.lower() in c.name.lower()
            ]

        if pagination.order == SortOrder.ASC:
            filtered.sort(key=lambda c: c.name)
        else:
            filtered.sort(key=lambda c: c.name, reverse=True)

        start = pagination.offset
        end = start + pagination.limit
        paginated = filtered[start:end]

        return [
            CategoryReadModel(
                category_id=c.category_id,
                name=c.name,
            )
            for c in paginated
        ]

    async def exists_by_name_in_shop(self, name: str, shop_id: ShopId) -> bool:
        return any(
            c.name == name and c.shop_id == shop_id
            for c in self.categories.values()
        )

    def next_id(self) -> CategoryId:
        return CategoryId(UUID(str(uuid7())))
