import uuid
from typing import Any

from backend.application.interfaces import ShopGateway
from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
)
from backend.application.vars import ShopId, UserId


class InMemoryShopGateway(ShopGateway):
    def __init__(
        self,
        linked_users: set[UserId] | None = None,
        shop_id: ShopId | None = None,
    ) -> None:
        self.linked_users = set(linked_users or [])
        self.shops: dict[ShopId, Any] = {}
        self.shop_id = shop_id

    async def relate_to_shop(self, user_id: UserId) -> bool:
        return user_id in self.linked_users

    async def create_shop(self, dto: CreateNewShopDTO) -> None:
        self.shops[dto.shop_id] = {"name": dto.name}
        self.linked_users.add(dto.user_id)

    def next_id(self) -> ShopId:
        return self.shop_id or ShopId(uuid.uuid4())
