from backend.application.errors import AuthorizationError
from backend.application.interfaces.idp import CurrentUserDTO, IdentityProvider
from backend.application.vars import ShopRole, UserId


class InMemoryIdentityProvider(IdentityProvider):
    def __init__(
        self, user_id: UserId | None = None, role: ShopRole = ShopRole.OWNER
    ) -> None:
        self.user_id = user_id
        self.role = role

    async def current_user_id(self) -> UserId | None:
        return self.user_id

    async def current_user(self) -> CurrentUserDTO:
        if self.user_id:
            return CurrentUserDTO(user_id=self.user_id, role=self.role)
        raise AuthorizationError
