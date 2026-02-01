from typing import cast
from uuid import UUID

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.category_gateway import (
    CategoryReadModel,
    GetCategoriesFilters,
)
from backend.application.vars import CategoryId, ShopId
from backend.infrastructure.persistence.tables import Category
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyCategoryGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> CategoryId:
        return CategoryId(UUID(str(uuid7())))

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

        if pagination.order == SortOrder.ASC:
            query = query.order_by(asc(Category.name), asc(Category.id))
        else:
            query = query.order_by(desc(Category.name), asc(Category.id))

        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [
            CategoryReadModel(
                category_id=CategoryId(cast("UUID", cast("object", row.id))),
                name=cast("str", cast("object", row.name)),
            )
            for row in rows
        ]

    async def exists_by_name_in_shop(self, name: str, shop_id: ShopId) -> bool:
        query = select(Category).where(
            Category.name == name,
            Category.shop_id == shop_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None
