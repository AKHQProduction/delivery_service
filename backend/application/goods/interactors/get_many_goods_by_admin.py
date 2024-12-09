import asyncio
import logging
from dataclasses import dataclass

from application.common.identity_provider import IdentityProvider
from application.common.interfaces.filters import Pagination
from application.goods.gateway import GoodsFilters, GoodsReader
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import OldShopGateway
from application.user.errors import UserNotFoundError
from entities.goods.models import Goods


@dataclass(frozen=True)
class GetManyGoodsByAdminInputData:
    pagination: Pagination
    filters: GoodsFilters


@dataclass(frozen=True)
class GetManyGoodsByAdminOutputData:
    total: int
    goods: list[Goods]


@dataclass
class GetManyGoodsByAdmin:
    identity_provider: IdentityProvider
    shop_reader: OldShopGateway
    goods_reader: GoodsReader

    async def __call__(
        self, data: GetManyGoodsByAdminInputData
    ) -> GetManyGoodsByAdminOutputData:
        actor = await self.identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        shop = await self.shop_reader.by_identity(actor.user_id)
        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        filters = GoodsFilters(
            shop_id=shop.shop_id, goods_type=data.filters.goods_type
        )

        get_goods_task = self.goods_reader.all(filters, data.pagination)
        total_goods_task = self.goods_reader.total(filters)

        goods, total_goods = await asyncio.gather(
            get_goods_task, total_goods_task
        )

        logging.info("Get goods for admin view")

        return GetManyGoodsByAdminOutputData(total_goods, goods)
