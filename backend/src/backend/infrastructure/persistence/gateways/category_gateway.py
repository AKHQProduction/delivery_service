from typing import cast
from uuid import UUID

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
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
from backend.infrastructure.persistence.tables import Category as CategoryDB
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyCategoryGateway(CategoryGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> CategoryId:
        return CategoryId(UUID(str(uuid7())))

    async def create_category(self, dto: CreateCategoryDTO) -> None:
        self._session.add(
            CategoryDB(
                id=dto.category_id,
                shop_id=dto.shop_id,
                name=dto.name,
            )
        )

    async def load(self, category_id: CategoryId) -> Category | None:
        row = await self._session.get(CategoryDB, category_id)
        if row:
            return self._to_entity(row)
        return None

    async def update(self, updated_category: Category) -> None:
        category_db = await self._session.get(
            CategoryDB, updated_category.category_id
        )
        if category_db:
            category_db.name = updated_category.name

    async def delete(self, category_id: CategoryId) -> None:
        category_db = await self._session.get(CategoryDB, category_id)
        if category_db:
            await self._session.delete(category_db)

    async def read_all(
        self, filters: GetCategoriesFilters, pagination: Pagination
    ) -> list[CategoryReadModel]:
        query = select(CategoryDB)

        if filters.shop_id:
            query = query.where(CategoryDB.shop_id == filters.shop_id)
        if filters.name:
            query = query.where(
                CategoryDB.name.ilike(f"%{escape_like(filters.name)}%")
            )

        if pagination.order == SortOrder.ASC:
            query = query.order_by(asc(CategoryDB.name), asc(CategoryDB.id))
        else:
            query = query.order_by(desc(CategoryDB.name), asc(CategoryDB.id))

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
        query = select(CategoryDB).where(
            CategoryDB.name == name,
            CategoryDB.shop_id == shop_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_entity(row: CategoryDB) -> Category:
        return Category(
            category_id=CategoryId(cast("UUID", cast("object", row.id))),
            shop_id=ShopId(cast("UUID", cast("object", row.shop_id))),
            name=cast("str", cast("object", row.name)),
        )
