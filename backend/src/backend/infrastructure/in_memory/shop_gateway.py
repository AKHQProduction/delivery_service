from backend.application.interfaces import ShopGateway
from backend.application.vars import UserId


class InMemoryShopGateway(ShopGateway):
    def __init__(self, linked_users: set[UserId] | None = None) -> None:
        self.linked_users = set(linked_users or [])

    async def relate_to_shop(self, user_id: UserId) -> bool:
        return user_id in self.linked_users
