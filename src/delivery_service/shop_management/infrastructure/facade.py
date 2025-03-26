from delivery_service.shop_management.application.ports.shop_provider import (
    ShopProvider,
)
from delivery_service.shop_management.public.api import ShopManagementAPI
from delivery_service.shop_management.public.shop_id import ShopID


class ShopManagementFacade(ShopManagementAPI):
    def __init__(self, shop_provider: ShopProvider) -> None:
        self._shop_provider = shop_provider

    async def get_current_shop_id(self) -> ShopID:
        return await self._shop_provider.get_current_shop_id()
