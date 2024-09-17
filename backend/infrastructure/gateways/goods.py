from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.goods.errors import GoodsAlreadyExistError
from application.goods.gateway import GoodsSaver
from entities.goods.models import Goods


class GoodsGateway(GoodsSaver):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, goods: Goods) -> None:
        self.session.add(goods)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise GoodsAlreadyExistError(goods_id=goods.goods_id) from error
