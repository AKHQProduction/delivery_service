import uuid

from backend.application.interfaces import (
    CreateUserViaTgDTO,
    ShopGateway,
    UserGateway,
)
from backend.application.interfaces.idp import IdentityProvider
from backend.application.vars import UserId


class InMemoryIdentityProvider(IdentityProvider):
    def __init__(self, user_id: UserId | None = None) -> None:
        self.user_id = user_id

    async def current_user_id(self) -> UserId | None:
        return self.user_id


class InMemoryUserGateway(UserGateway):
    def __init__(self) -> None:
        self.users: set[UserId] = set()

    async def create_user_via_tg(self, data: CreateUserViaTgDTO) -> None:
        self.users.add(data.user_id)

    def next_id(self) -> UserId:
        return UserId(uuid.uuid4())


class InMemoryShopGateway(ShopGateway):
    def __init__(self, linked_users: set[UserId] | None = None) -> None:
        self.linked_users = set(linked_users or [])

    async def relate_to_shop(self, user_id: UserId) -> bool:
        return user_id in self.linked_users
