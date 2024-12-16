from application.commands.shop import ShopSaver
from application.common.errors import ShopAlreadyExistsError
from application.common.persistence import (
    Pagination,
    ShopGateway,
    ShopGatewayFilters,
)
from entities.shop.models import Shop, ShopId
from entities.shop.value_objects import (
    DeliveryDistance,
    ShopLocation,
    ShopTitle,
    ShopToken,
)
from entities.user.models import UserId


class FakeShopGateway(ShopGateway, ShopSaver):
    def __init__(self):
        self.shops: dict[int, Shop] = {
            1234567898: Shop(
                shop_id=ShopId(1234567898),
                title=ShopTitle("TestShop"),
                token=ShopToken(
                    "1234567898:AAGzbSDaSqQ-mOQEJfPLE1wBH0Y4J40xT48"
                ),
                delivery_distance=DeliveryDistance(50),
                location=ShopLocation(48.5035903, 31.0787222),
            ),
        }

        self.saved = False
        self.deleted = False

    async def save(self, shop: Shop) -> None:
        shop_in_memory = await self.load_with_id(shop.shop_id)

        if shop_in_memory:
            raise ShopAlreadyExistsError(shop.shop_id)

        self.shops[shop.shop_id] = shop
        self.saved = True

    async def load_with_id(self, shop_id: ShopId) -> Shop | None:
        return self.shops.get(shop_id, None)

    async def load_with_identity(self, user_id: UserId) -> Shop | None:
        if user_id in (1, 3):
            return self.shops.get(1234567898)
        return None

    async def delete(self, shop_id: ShopId) -> None:
        shop = self.shops.get(shop_id, None)

        if shop:
            del self.shops[shop_id]

        self.deleted = True

    async def load_many(
        self, filters: ShopGatewayFilters, pagination: Pagination
    ) -> list[Shop]:
        pass

    async def total(self, filters: ShopGatewayFilters) -> int:
        return len(self.shops)
