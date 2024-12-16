from typing import Sequence
from uuid import UUID

from sqlalchemy import RowMapping, Select, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.persistence.goods import (
    GoodsGateway,
    GoodsReader,
    GoodsReaderFilters,
    GoodsView,
)
from entities.goods.models import Goods, GoodsId
from entities.shop.models import ShopId
from infrastructure.persistence.models.goods import goods_table


class SQLAlchemyGoodsMapper(GoodsGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def is_exist(self, title: str, shop_id: ShopId) -> bool:
        query = select(exists()).where(
            goods_table.c.title == title, goods_table.c.shop_id == shop_id
        )

        result = await self.session.execute(query)

        return result.scalar()

    async def load_with_id(self, goods_id: GoodsId) -> Goods | None:
        return await self.session.get(Goods, goods_id)


class SQLAlchemyGoodsReader(GoodsReader):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    @staticmethod
    def _load_view(row: RowMapping) -> GoodsView:
        return GoodsView(
            goods_id=row.goods_id,
            title=row.title,
            price=row.price,
        )

    @staticmethod
    def _select_goods_view() -> Select:
        return select(
            goods_table.c.goods_id, goods_table.c.title, goods_table.c.price
        )

    @staticmethod
    def _set_filters(query: Select, filters: GoodsReaderFilters) -> Select:
        query = query.where(goods_table.c.shop_id == filters.shop_id)

        if filters.goods_type:
            query = query.where(goods_table.c.goods_type == filters.goods_type)

        return query

    async def read_with_id(self, goods_id: UUID) -> Goods | None:
        query = self._select_goods_view()

        query = query.where(goods_table.c.goods_id == goods_id)

        result = await self.session.execute(query)
        row = result.mappings().one_or_none()

        return None if not row else self._load_view(row)

    async def read_many(
        self, filters: GoodsReaderFilters
    ) -> Sequence[GoodsView]:
        query = self._select_goods_view()

        query = self._set_filters(query, filters)

        rows = await self.session.execute(query)

        return [self._load_view(row) for row in rows.mappings()]
