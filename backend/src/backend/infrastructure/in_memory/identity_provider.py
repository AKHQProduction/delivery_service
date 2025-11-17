from backend.application.errors import AuthorizationError
from backend.application.interfaces.idp import CurrentUserDTO, IdentityProvider
from backend.application.vars import ShopId, ShopRole, UserId


class InMemoryIdentityProvider(IdentityProvider):
    def __init__(
        self,
        user_id: UserId | None = None,
        role: ShopRole = ShopRole.OWNER,
        shop_id: ShopId | None = None,
    ) -> None:
        self.user_id = user_id
        self.role = role
        self.shop_id = shop_id

    async def current_user_id(self) -> UserId | None:
        return self.user_id

    async def current_user(self) -> CurrentUserDTO:
        if self.user_id and self.shop_id:
            return CurrentUserDTO(
                user_id=self.user_id, role=self.role, shop_id=self.shop_id
            )
        raise AuthorizationError
