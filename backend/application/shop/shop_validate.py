from application.shop.errors import ShopIsNotActiveError, ShopIsNotExistError
from application.shop.gateway import ShopReader
from entities.shop.models import ShopId


class ShopValidationService:
    def __init__(self, shop_reader: ShopReader):
        self._shop_reader = shop_reader

    async def check_shop(self, shop_id: ShopId):
        shop = await self._shop_reader.by_id(shop_id)

        if not shop:
            raise ShopIsNotExistError(shop_id)

        if not shop.is_active:
            raise ShopIsNotActiveError(shop_id)
