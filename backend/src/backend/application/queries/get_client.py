from backend.application.errors import EntityNotFoundError
from backend.application.interfaces import ClientGateway, IdentityProvider
from backend.application.interfaces.gateways.client_gateway import (
    ClientReadModel,
)
from backend.application.vars import ClientId


class GetClientQueryHandler:
    def __init__(
        self, idp: IdentityProvider, client_gateway: ClientGateway
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway

    async def handle(self, client_id: ClientId) -> ClientReadModel:
        await self._idp.current_user()

        if client := await self._client_gateway.read(client_id):
            return client
        raise EntityNotFoundError(entity="Client")
