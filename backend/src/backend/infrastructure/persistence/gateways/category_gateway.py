from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from backend.application.dto.gateways import Pagination
from backend.application.dto.gateways.category_gateway import (
    CategoryReadModel,
    GetCategoriesFilters,
)
from backend.application.vars import CategoryId, ShopId
from backend.infrastructure.persistence.tables import Category
from backend.infrastructure.persistence.utils.cast import mapped_cast
from backend.infrastructure.persistence.utils.escape import escape_like
from backend.infrastructure.persistence.utils.sorting import apply_sorting


class SQLAlchemyCategoryGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> CategoryId:
        return CategoryId(uuid7())

    def save(self, category: Category) -> None:
        self._session.add(category)

    async def load(self, category_id: CategoryId) -> Category | None:
        return await self._session.get(Category, category_id)

    async def delete(self, category: Category) -> None:
        await self._session.delete(category)

    async def read_all(
        self, filters: GetCategoriesFilters, pagination: Pagination
    ) -> list[CategoryReadModel]:
        query = select(Category)

        if filters.shop_id:
            query = query.where(Category.shop_id == filters.shop_id)
        if filters.name:
            query = query.where(
                Category.name.ilike(f"%{escape_like(filters.name)}%")
            )

        query = apply_sorting(query, Category.name, Category.id, pagination)

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [
            CategoryReadModel(
                category_id=CategoryId(mapped_cast(UUID, row.id)),
                name=mapped_cast(str, row.name),
            )
            for row in rows
        ]

    async def exists_by_name_in_shop(self, name: str, shop_id: ShopId) -> bool:
        query = select(
            select(Category.id)
            .where(Category.name == name, Category.shop_id == shop_id)
            .exists()
        )
        result = await self._session.execute(query)
        return result.scalar_one()
