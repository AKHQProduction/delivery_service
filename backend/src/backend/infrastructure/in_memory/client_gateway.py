import uuid

from backend.application.interfaces.gateways.client_gateway import (
    ClientGateway,
    CreateClientDTO,
)
from backend.application.vars import ClientId


class InMemoryClientGateway(ClientGateway):
    def __init__(self, client_id: ClientId | None = None) -> None:
        self.clients: dict[ClientId, CreateClientDTO] = {}
        self.client_id = client_id

    async def create_client(self, dto: CreateClientDTO) -> None:
        self.clients[dto.client_id] = dto

    def next_id(self) -> ClientId:
        return self.client_id or ClientId(uuid.uuid4())
