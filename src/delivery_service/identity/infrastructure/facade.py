from delivery_service.identity.application.ports.idp import IdentityProvider
from delivery_service.identity.public.api import IdentityPublicAPI
from delivery_service.identity.public.identity_id import UserID


class IdentityFacade(IdentityPublicAPI):
    def __init__(self, identity_provider: IdentityProvider) -> None:
        self._idp = identity_provider

    async def get_current_identity(self) -> UserID:
        return await self._idp.get_current_user_id()
