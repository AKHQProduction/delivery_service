from typing import Sequence

from sqlalchemy import RowMapping, Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.product_gateway import (
    ProductGateway,
    ProductGatewayFilters,
    ProductReadModel,
)
from delivery_service.domain.products.product import ProductID
from delivery_service.infrastructure.persistence.tables import PRODUCTS_TABLE


class SQLAlchemyProductGateway(ProductGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _set_filters(query: Select, filters: ProductGatewayFilters) -> Select:
        if filters.shop_id is not None:
            query = query.where(
                and_(PRODUCTS_TABLE.c.shop_id == filters.shop_id)
            )

        return query

    @staticmethod
    def _map_row_to_read_model(row: RowMapping) -> ProductReadModel:
        return ProductReadModel(
            product_id=row.product_id,
            title=row.title,
            price=row.price,
            product_type=row.product_type,
        )

    @staticmethod
    def _select_rows() -> Select:
        return select(
            PRODUCTS_TABLE.c.id.label("product_id"),
            PRODUCTS_TABLE.c.title.label("title"),
            PRODUCTS_TABLE.c.price.label("price"),
            PRODUCTS_TABLE.c.product_type.label("product_type"),
        )

    async def read_with_id(
        self, product_id: ProductID
    ) -> ProductReadModel | None:
        query = self._select_rows()
        query = query.where(and_(PRODUCTS_TABLE.c.id == product_id))

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return self._map_row_to_read_model(row) if row else None

    async def read_all_products(
        self, filters: ProductGatewayFilters | None = None
    ) -> Sequence[ProductReadModel]:
        query = self._select_rows()

        if filters:
            query = self._set_filters(query=query, filters=filters)

        result = await self._session.execute(query)
        return [self._map_row_to_read_model(row) for row in result.mappings()]

    async def total(self, filters: ProductGatewayFilters | None = None) -> int:
        query = select(func.count(PRODUCTS_TABLE.c.id))

        if filters:
            query = self._set_filters(query=query, filters=filters)

        result = await self._session.execute(query)
        return result.scalar_one()
