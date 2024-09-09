from application.common.identity_provider import IdentityProvider
from entities.user.models import User, UserId
from tests.mocks.gateways.user import FakeUserGateway


class FakeIdentityProvider(IdentityProvider):
    def __init__(self, user_id: UserId, user_gateway: FakeUserGateway):
        self._user_id = user_id
        self._user_gateway = user_gateway

    async def get_user(self) -> User:
        return await self._user_gateway.by_id(self._user_id)
