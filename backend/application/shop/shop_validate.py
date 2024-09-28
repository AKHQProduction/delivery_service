from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopReader
from entities.shop.models import Shop, ShopId


class ShopValidationService:
    def __init__(self, shop_reader: ShopReader):
        self._shop_reader = shop_reader

    async def check_shop(self, shop_id: ShopId) -> Shop:
        shop = await self._shop_reader.by_id(shop_id)

        if not shop:
            raise ShopNotFoundError(shop_id)

        if not shop.is_active:
            raise ShopIsNotActiveError(shop_id)

        return shop
