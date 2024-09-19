import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.interactor import Interactor
from application.goods.errors import GoodsIsNotExistError
from application.goods.gateway import GoodsReader
from entities.goods.models import Goods, GoodsId


@dataclass(frozen=True)
class GetGoodsInputData:
    goods_id: UUID


class GetGoods(Interactor[GetGoodsInputData, Goods]):
    def __init__(self, goods_reader: GoodsReader):
        self._goods_reader = goods_reader

    async def __call__(self, data: GetGoodsInputData) -> Goods:
        goods_id = GoodsId(data.goods_id)
        goods = await self._goods_reader.by_id(goods_id)

        if not goods:
            logging.info("GetGoods: goods with id=%s not found", goods_id)
            raise GoodsIsNotExistError(data.goods_id)

        logging.info("GetGoods: successfully get goods with id=%s", goods_id)
        return goods
