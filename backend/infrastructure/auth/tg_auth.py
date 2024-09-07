from application.user.gateway import UserReader
from application.common.identity_provider import IdentityProvider
from entities.user.models import User, UserId


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
