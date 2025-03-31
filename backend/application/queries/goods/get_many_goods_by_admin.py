from dataclasses import dataclass
from typing import Sequence

from application.common.identity_provider import IdentityProvider
from application.common.persistence.goods import (
    GoodsReader,
    GoodsReaderFilters,
)
from application.common.persistence.shop import ShopGateway
from application.common.persistence.view_models import GoodsView
from application.common.validators import validate_shop, validate_user


@dataclass(frozen=True)
class GetManyGoodsByAdminQuery:
    filters: GoodsReaderFilters


@dataclass
class GetManyGoodsByAdminQueryHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    goods_reader: GoodsReader

    async def __call__(
        self, data: GetManyGoodsByAdminQuery
    ) -> Sequence[GoodsView]:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        filters = GoodsReaderFilters(
            shop_id=shop.oid, goods_type=data.filters.goods_type
        )

        return await self.goods_reader.read_many(filters)
