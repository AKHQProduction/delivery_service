from dataclasses import dataclass

from application.shop.errors import ShopNotFoundError
from application.shop.gateway import ShopInfo, ShopReader
from entities.shop.models import ShopId


@dataclass(frozen=True)
class GetShopInfoInputData:
    shop_id: int


@dataclass
class GetShopInfo:
    shop_reader: ShopReader

    async def __call__(self, data: GetShopInfoInputData) -> ShopInfo | None:
        shop_info = await self.shop_reader.get_by_id(ShopId(data.shop_id))

        if not shop_info:
            raise ShopNotFoundError(data.shop_id)
        return shop_info
