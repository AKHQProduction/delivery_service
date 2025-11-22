import uuid
from typing import Any

from backend.application.interfaces import ShopGateway
from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
    ShopEmployee,
)
from backend.application.vars import ShopId, ShopRole, UserId


class InMemoryShopGateway(ShopGateway):
    def __init__(
        self,
        linked_users: set[UserId] | None = None,
        shop_id: ShopId | None = None,
    ) -> None:
        self.linked_users = set(linked_users or [])
        self.shops: dict[ShopId, Any] = {}
        self.shop_id = shop_id
        self.employees: dict[UserId, ShopEmployee] = {}

    async def relate_to_shop(self, user_id: UserId) -> bool:
        return user_id in self.linked_users

    async def create_shop(self, dto: CreateNewShopDTO) -> None:
        self.shops[dto.shop_id] = {"name": dto.shop_name}
        self.linked_users.add(dto.user_id)
        self.employees[dto.user_id] = ShopEmployee(
            user_id=dto.user_id,
            shop_id=dto.shop_id,
            full_name=dto.owner_name,
            role=ShopRole.OWNER,
        )

    async def get_shop_employee(self, user_id: UserId) -> ShopEmployee | None:
        return self.employees.get(user_id)

    def next_id(self) -> ShopId:
        return self.shop_id or ShopId(uuid.uuid4())
