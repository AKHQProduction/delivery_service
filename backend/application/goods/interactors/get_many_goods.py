import logging
from dataclasses import dataclass

from application.common.input_data import Pagination
from application.common.interactor import Interactor
from application.goods.gateway import GetManyGoodsFilters, GoodsReader
from entities.goods.models import Goods


@dataclass(frozen=True)
class GetManyGoodsInputData:
    pagination: Pagination
    filters: GetManyGoodsFilters


@dataclass(frozen=True)
class GetManyGoodsOutputData:
    total: int
    goods: list[Goods]


class GetManyGoods(Interactor[GetManyGoodsInputData, GetManyGoodsOutputData]):
    def __init__(self, goods_reader: GoodsReader):
        self._goods_reader = goods_reader

    async def __call__(
        self, data: GetManyGoodsInputData
    ) -> GetManyGoodsOutputData:
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
