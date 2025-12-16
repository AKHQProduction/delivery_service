import uuid

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.client_gateway import (
    ClientDM,
    ClientGateway,
    ClientReadModel,
    CreateClientDTO,
    GetClientsFilters,
)
from backend.application.vars import ClientId


class InMemoryClientGateway(ClientGateway):
    def __init__(self, client_id: ClientId | None = None) -> None:
        self.clients: dict[ClientId, ClientDM] = {}
        self.client_id = client_id
        self.updated = False

    async def create_client(self, dto: CreateClientDTO) -> None:
        client = ClientDM(
            client_id=dto.client_id,
            shop_id=dto.shop_id,
            full_name=dto.full_name,
            phones=dto.phones,
            addresses=dto.addresses,
            custom_id=dto.custom_id,
        )
        self.clients[dto.client_id] = client

    async def load(self, client_id: ClientId) -> ClientDM | None:
        entity = self.clients.get(client_id)
        if not entity:
            return None
        return ClientDM(
            client_id=entity.client_id,
            shop_id=entity.shop_id,
            full_name=entity.full_name,
            phones=entity.phones,
            addresses=entity.addresses,
            custom_id=entity.custom_id,
        )

    async def read(self, client_id: ClientId) -> ClientReadModel | None:
        dto = self.clients.get(client_id)
        if dto is None:
            return None

        return ClientReadModel(
            client_id=dto.client_id,
            full_name=dto.full_name,
            phones=dto.phones,
            addresses=dto.addresses,
            custom_id=dto.custom_id,
        )

    async def read_all(
        self,
        filters: GetClientsFilters,
        pagination: Pagination,
    ) -> list[ClientReadModel]:
        result = []

        for dto in self.clients.values():
            if filters.shop_id and dto.shop_id != filters.shop_id:
                continue

            if (
                filters.full_name
                and filters.full_name.lower() not in dto.full_name.lower()
            ):
                continue

            if filters.custom_id and dto.custom_id != filters.custom_id:
                continue

            if filters.phone:
                phone_found = any(
                    filters.phone in phone.number for phone in dto.phones
                )
                if not phone_found:
                    continue

            result.append(
                ClientReadModel(
                    client_id=dto.client_id,
                    full_name=dto.full_name,
                    phones=dto.phones,
                    addresses=dto.addresses,
                    custom_id=dto.custom_id,
                )
            )

        if pagination.order == SortOrder.ASC:
            result.sort(key=lambda x: x.full_name)
        else:
            result.sort(key=lambda x: x.full_name, reverse=True)

        start = pagination.offset
        end = pagination.offset + pagination.limit
        return result[start:end]

    async def delete(self, client_id: ClientId) -> None:
        if client_id in self.clients:
            del self.clients[client_id]

    async def update(self, updated_client: ClientDM) -> None:
        if updated_client.client_id in self.clients:
            self.clients[updated_client.client_id] = updated_client
            self.updated = True

    def next_id(self) -> ClientId:
        return self.client_id or ClientId(uuid.uuid4())

    async def exists_with_number(self, number: str) -> bool:
        for client in self.clients.values():
            if any(phone.number == number for phone in client.phones):
                return True
        return False
