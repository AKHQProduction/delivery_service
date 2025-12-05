from uuid import UUID

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    ClientGateway,
    ClientReadModel,
    CreateClientDTO,
    GetClientsFilters,
    PhoneDTO,
)
from backend.application.vars import AddressType, ClientId
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

    async def read(self, client_id: ClientId) -> ClientReadModel | None:
        query = (
            select(Client)
            .where(Client.id == client_id)
            .options(
                selectinload(Client.phones), selectinload(Client.addresses)
            )
        )

        result = await self._session.execute(query)
        client = result.scalar_one_or_none()

        if client is None:
            return None

        phones = [
            PhoneDTO(number=phone.number, is_primary=phone.is_primary)
            for phone in client.phones
        ]

        addresses = [
            AddressDTO(
                street=address.street,
                house=address.house,
                address_type=AddressType(address.address_type),
                apartment=address.apartment,
                entrance=address.entrance,
                floor=address.floor,
                intercom=address.intercom,
                is_primary=address.is_primary,
            )
            for address in client.addresses
        ]

        return ClientReadModel(
            client_id=ClientId(client.id),
            full_name=client.full_name,
            phones=phones,
            addresses=addresses,
            custom_id=client.custom_id,
        )

    async def read_all(
        self,
        filters: GetClientsFilters,
        pagination: Pagination,
    ) -> list[ClientReadModel]:
        query = select(Client).options(
            selectinload(Client.phones), selectinload(Client.addresses)
        )

        if filters.shop_id:
            query = query.where(Client.shop_id == filters.shop_id)

        if filters.full_name:
            query = query.where(
                Client.full_name.ilike(f"%{filters.full_name}%")
            )

        if filters.custom_id:
            query = query.where(Client.custom_id == filters.custom_id)

        if filters.phone:
            query = query.join(ClientPhone).where(
                ClientPhone.number.ilike(f"%{filters.phone}%")
            )

        if pagination.order == SortOrder.ASC:
            query = query.order_by(asc(Client.full_name))
        else:
            query = query.order_by(desc(Client.full_name))

        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        clients = result.scalars().unique().all()

        return [
            ClientReadModel(
                client_id=ClientId(client.id),
                full_name=client.full_name,
                phones=[
                    PhoneDTO(number=phone.number, is_primary=phone.is_primary)
                    for phone in client.phones
                ],
                addresses=[
                    AddressDTO(
                        street=address.street,
                        house=address.house,
                        address_type=AddressType(address.address_type),
                        apartment=address.apartment,
                        entrance=address.entrance,
                        floor=address.floor,
                        intercom=address.intercom,
                        is_primary=address.is_primary,
                    )
                    for address in client.addresses
                ],
                custom_id=client.custom_id,
            )
            for client in clients
        ]

    def next_id(self) -> ClientId:
        return ClientId(UUID(str(uuid7())))
