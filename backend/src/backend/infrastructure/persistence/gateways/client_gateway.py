from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces.gateways.client_gateway import (
    ClientGateway,
    CreateClientDTO,
)
from backend.application.vars import ClientId
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)


class SQLAlchemyClientGateway(ClientGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_client(self, dto: CreateClientDTO) -> None:
        phones = [
            ClientPhone(
                number=phone.number,
                is_primary=idx == 0,
                shop_id=dto.shop_id,
            )
            for idx, phone in enumerate(dto.phones)
        ]

        addresses = [
            ClientAddress(
                street=address.street,
                house=address.house,
                address_type=address.address_type.value,
                apartment=address.apartment,
                entrance=address.entrance,
                floor=address.floor,
                intercom=address.intercom,
                is_primary=idx == 0,
            )
            for idx, address in enumerate(dto.addresses)
        ]

        new_client = Client(
            id=dto.client_id,
            custom_id=dto.custom_id,
            full_name=dto.full_name,
            shop_id=dto.shop_id,
            phones=phones,
            addresses=addresses,
        )

        self._session.add(new_client)

    def next_id(self) -> ClientId:
        return ClientId(UUID(str(uuid7())))
