from backend.application.dto.gateways.client_gateway import (
    ClientReadModel,
)
from backend.application.errors import EntityNotFoundError
from backend.application.vars import ClientId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyClientGateway


class GetClientQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway

    async def handle(self, client_id: ClientId) -> ClientReadModel:
        await self._idp.current_user()

        if client := await self._client_gateway.read(client_id):
            return client
        raise EntityNotFoundError(entity="Client")
