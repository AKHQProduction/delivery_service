from application.common.gateways.role import RoleReader
from application.common.gateways.user import UserReader
from application.common.identity_provider import IdentityProvider
from domain.entities.role import Role
from domain.entities.user import User
from domain.value_objects.user_id import UserId


class TgIdentityProvider(IdentityProvider):
    def __init__(
            self,
            user_id: int,
            user_gateway: UserReader,
            role_gateway: RoleReader
    ):
        self._user_id = user_id
        self._user_gateway = user_gateway
        self._role_gateway = role_gateway

    async def get_user(self) -> User:
        return await self._user_gateway.by_id(UserId(self._user_id))

    async def get_user_roles(self) -> list[Role]:
        return await self._role_gateway.by_id(UserId(self._user_id))
