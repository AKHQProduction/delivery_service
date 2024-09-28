import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.interactor import Interactor
from application.goods.errors import GoodsNotFoundError
from application.goods.gateway import GoodsReader
from application.shop.gateway import ShopReader
from application.shop.shop_validate import ShopValidationService
from entities.goods.models import Goods, GoodsId
from entities.shop.models import ShopId


@dataclass(frozen=True)
class GetGoodsInputData:
    goods_id: UUID
    shop_id: int | None = None


class GetGoods(Interactor[GetGoodsInputData, Goods]):
    def __init__(
        self,
        goods_reader: GoodsReader,
        shop_reader: ShopReader,
        shop_validation: ShopValidationService,
    ):
        self._goods_reader = goods_reader
        self._shop_reader = shop_reader
        self._shop_validation = shop_validation

    async def __call__(self, data: GetGoodsInputData) -> Goods:
        if data.shop_id:
            await self._shop_validation.check_shop(ShopId(data.shop_id))

        goods_id = GoodsId(data.goods_id)
        goods = await self._goods_reader.by_id(goods_id)

        if not goods:
            logging.info("GetGoods: goods with id=%s not found", goods_id)
            raise GoodsNotFoundError(data.goods_id)

        logging.info("GetGoods: successfully get goods with id=%s", goods_id)
        return goods
