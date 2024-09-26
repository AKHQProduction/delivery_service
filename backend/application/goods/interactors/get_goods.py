import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.interactor import Interactor
from application.goods.errors import GoodsIsNotExistError
from application.goods.gateway import GoodsReader
from application.shop.errors import ShopIsNotActiveError, ShopIsNotExistError
from application.shop.gateway import ShopReader
from entities.goods.models import Goods, GoodsId
from entities.shop.models import ShopId


@dataclass(frozen=True)
class GetGoodsInputData:
    goods_id: UUID
    shop_id: int | None = None


class GetGoods(Interactor[GetGoodsInputData, Goods]):
    def __init__(self, goods_reader: GoodsReader, shop_reader: ShopReader):
        self._goods_reader = goods_reader
        self._shop_reader = shop_reader

    async def __call__(self, data: GetGoodsInputData) -> Goods:
        if data.shop_id:
            shop = await self._shop_reader.by_id(ShopId(data.shop_id))

            if not shop:
                raise ShopIsNotExistError(data.shop_id)

            if not shop.is_active:
                raise ShopIsNotActiveError(data.shop_id)

        goods_id = GoodsId(data.goods_id)
        goods = await self._goods_reader.by_id(goods_id)

        if not goods:
            logging.info("GetGoods: goods with id=%s not found", goods_id)
            raise GoodsIsNotExistError(data.goods_id)

        logging.info("GetGoods: successfully get goods with id=%s", goods_id)
        return goods
