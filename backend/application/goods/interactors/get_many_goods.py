import logging
from dataclasses import dataclass

from application.common.input_data import Pagination
from application.common.interactor import Interactor
from application.goods.gateway import GetManyGoodsFilters, GoodsReader
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopReader
from entities.goods.models import Goods
from entities.shop.models import ShopId


@dataclass(frozen=True)
class GetManyGoodsInputData:
    pagination: Pagination
    filters: GetManyGoodsFilters


@dataclass(frozen=True)
class GetManyGoodsOutputData:
    total: int
    goods: list[Goods]


class GetManyGoods(Interactor[GetManyGoodsInputData, GetManyGoodsOutputData]):
    def __init__(
        self,
        goods_reader: GoodsReader,
        shop_reader: ShopReader,
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

        total_goods = await self._goods_reader.total(data.filters)
        goods = await self._goods_reader.all(data.filters, data.pagination)

        logging.info(
            "Get all goods",
            extra={
                "goods": goods,
                "pagination": data.pagination,
                "filters": data.filters,
            },
        )

        return GetManyGoodsOutputData(total=total_goods, goods=goods)
