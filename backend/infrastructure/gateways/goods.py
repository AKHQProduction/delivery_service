from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.input_data import Pagination, SortOrder
from application.goods.errors import GoodsAlreadyExistError
from application.goods.gateway import (
    GoodsFilters,
    GoodsReader,
    GoodsSaver,
)
from entities.goods.models import Goods, GoodsId
from infrastructure.persistence.models.goods import goods_table


class GoodsGateway(GoodsSaver, GoodsReader):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, goods: Goods) -> None:
        self.session.add(goods)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise GoodsAlreadyExistError(goods_id=goods.goods_id) from error

    async def by_id(self, goods_id: GoodsId) -> Goods | None:
        query = select(Goods).where(goods_table.c.goods_id == goods_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def all(
        self, filters: GoodsFilters, pagination: Pagination
    ) -> list[Goods]:
        query = select(Goods).where(goods_table.c.shop_id == filters.shop_id)

        if filters.goods_type:
            query = query.where(goods_table.c.goods_type == filters.goods_type)

        if pagination.order is SortOrder.ASC:
            query = query.order_by(goods_table.c.created_at.asc())
        else:
            query = query.order_by(goods_table.c.created_at.desc())

        if pagination.offset is not None:
            query = query.offset(pagination.offset)
        if pagination.limit is not None:
            query = query.limit(pagination.limit)

        result = await self.session.scalars(query)

        return list(result.all())

    async def total(self, filters: GoodsFilters) -> int:
        query = select(func.count(goods_table.c.goods_id))

        if filters.shop_id:
            query = query.where(goods_table.c.shop_id == filters.shop_id)

        total: int = await self.session.scalar(query)

        return total

    async def delete(self, goods: Goods) -> None:
        query = delete(Goods).where(goods_table.c.goods_id == goods.goods_id)

        await self.session.execute(query)
