import asyncio
import logging
from dataclasses import dataclass

from application.common.interactor import Interactor
from application.common.interfaces.filters import Pagination
from application.goods.gateway import GoodsFilters, GoodsReader
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopGateway
from entities.goods.models import Goods
from entities.shop.models import ShopId


@dataclass(frozen=True)
class GetManyGoodsInputData:
    pagination: Pagination
    filters: GoodsFilters


@dataclass(frozen=True)
class GetManyGoodsOutputData:
    total: int
    goods: list[Goods]


class GetManyGoods(Interactor[GetManyGoodsInputData, GetManyGoodsOutputData]):
    def __init__(
        self,
        goods_reader: GoodsReader,
        shop_reader: ShopGateway,
    ):
        self._goods_reader = goods_reader
        self._shop_reader = shop_reader

    async def __call__(
        self, data: GetManyGoodsInputData
    ) -> GetManyGoodsOutputData:
        shop_id = data.filters.shop_id

        shop = await self._shop_reader.by_id(ShopId(shop_id))
        if not shop:
            raise ShopNotFoundError(shop_id)
        if not shop.is_active:
            raise ShopIsNotActiveError(shop_id)

        total_goods_task = self._goods_reader.total(data.filters)
        get_goods_task = self._goods_reader.all(data.filters, data.pagination)

        total_goods, goods = await asyncio.gather(
            total_goods_task, get_goods_task
        )

        logging.info(
            "Fetched %s goods with filters %s and pagination %s",
            total_goods,
            data.filters,
            data.pagination,
            extra={
                "goods_count": len(goods),
                "filters": data.filters,
                "pagination": data.pagination,
            },
        )

        return GetManyGoodsOutputData(total=total_goods, goods=goods)
