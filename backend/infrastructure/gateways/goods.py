from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.goods.errors import GoodsAlreadyExistError
from application.goods.gateway import GoodsReader, GoodsSaver
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

    async def delete(self, goods: Goods) -> None:
        query = delete(Goods).where(goods_table.c.goods_id == goods.goods_id)

        await self.session.execute(query)
