from typing import cast
from uuid import UUID

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils.compat import uuid7

from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.product_gateway import (
    GetProductsFilters,
    ProductReadModel,
)
from backend.application.vars import CategoryId, ProductId, ShopId
from backend.infrastructure.persistence.tables import Product
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyProductGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> ProductId:
        return ProductId(uuid7())

    def save(self, product: Product) -> None:
        self._session.add(product)

    async def load(self, product_id: ProductId) -> Product | None:
        return await self._session.get(Product, product_id)

    async def load_many(self, product_ids: list[ProductId]) -> list[Product]:
        if not product_ids:
            return []

        query = select(Product).where(Product.id.in_(product_ids))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def delete(self, product: Product) -> None:
        await self._session.delete(product)

    async def read(
        self, product_id: ProductId, shop_id: ShopId
    ) -> ProductReadModel | None:
        query = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.category))
        )
        result = await self._session.execute(query)
        row = result.scalar_one_or_none()
        if row:
            return ProductReadModel(
                product_id=ProductId(cast("UUID", cast("object", row.id))),
                name=cast("str", cast("object", row.name)),
                category_id=CategoryId(row.category_id)
                if row.category_id
                else None,
                category_name=row.category.name if row.category else None,
                price=int(row.price),
            )
        return None

    async def read_all(
        self,
        filters: GetProductsFilters,
        pagination: Pagination,
    ) -> list[ProductReadModel]:
        query = select(Product).options(selectinload(Product.category))

        if filters.shop_id:
            query = query.where(Product.shop_id == filters.shop_id)
        if filters.name:
            query = query.where(
                Product.name.ilike(f"%{escape_like(filters.name)}%")
            )

        if pagination.order == SortOrder.ASC:
            query = query.order_by(asc(Product.name), asc(Product.id))
        else:
            query = query.order_by(desc(Product.name), asc(Product.id))

        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [
            ProductReadModel(
                product_id=ProductId(cast("UUID", cast("object", row.id))),
                name=cast("str", cast("object", row.name)),
                category_id=CategoryId(row.category_id)
                if row.category_id
                else None,
                category_name=row.category.name if row.category else None,
                price=int(row.price),
            )
            for row in rows
        ]
