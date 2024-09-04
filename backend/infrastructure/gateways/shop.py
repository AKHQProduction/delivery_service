from application.shop.gateway import ShopReader, ShopSaver
from entities.shop.model import Shop, ShopId


class InMemoryShopGateway(ShopSaver, ShopReader):
    def __init__(self):
        self._shops: dict[int, Shop] = {}

    async def by_id(self, shop_id: ShopId) -> Shop | None:
        return self._shops.get(shop_id)

    async def save(self, shop: Shop) -> None:
        self._shops[shop.shop_id] = shop

    async def update(self, shop: Shop) -> None:
        self._shops[shop.shop_id] = shop
