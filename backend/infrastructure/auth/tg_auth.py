from application.user.gateways.user import UserReader
from application.common.identity_provider import IdentityProvider
from domain.user.entity.user import RoleName, User
from domain.user.value_objects.user_id import UserId


class TgIdentityProvider(IdentityProvider):
    def __init__(
            self,
            user_id: int,
            user_gateway: UserReader,
    ):
        self._user_id = user_id
        self._user_gateway = user_gateway

    async def get_user(self) -> User:
        return await self._user_gateway.by_id(UserId(self._user_id))

    async def get_user_role(self) -> RoleName:
        user = await self.get_user()

        return user.role
