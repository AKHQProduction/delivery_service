from uuid import UUID

from sqlalchemy import asc, delete, desc, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    ClientDM,
    ClientGateway,
    ClientReadModel,
    CreateClientDTO,
    GetClientsFilters,
    PhoneDTO,
)
from backend.application.vars import AddressType, ClientId, ShopId
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

    async def load(self, client_id: ClientId) -> ClientDM | None:
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

        return ClientDM(
            client_id=ClientId(client.id),
            custom_id=client.custom_id,
            shop_id=ShopId(client.shop_id),
            full_name=client.full_name,
            phones=phones,
            addresses=addresses,
        )

    async def delete(self, client_id: ClientId) -> None:
        client_db = await self._session.get(Client, client_id)
        if client_db:
            await self._session.delete(client_db)

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

    async def update(self, updated_client: ClientDM) -> None:
        client = await self._session.get(Client, updated_client.client_id)
        if client:
            client.custom_id = updated_client.custom_id
            client.full_name = updated_client.full_name

            # Update phones
            await self._session.execute(
                delete(ClientPhone).where(
                    ClientPhone.client_id == updated_client.client_id
                )
            )
            for idx, phone_dto in enumerate(updated_client.phones):
                new_phone = ClientPhone(
                    number=phone_dto.number,
                    is_primary=(idx == 0),
                    client_id=updated_client.client_id,
                    shop_id=updated_client.shop_id,
                )
                self._session.add(new_phone)

            await self._session.execute(
                delete(ClientAddress).where(
                    ClientAddress.client_id == updated_client.client_id
                )
            )
            for idx, address_dto in enumerate(updated_client.addresses):
                new_address = ClientAddress(
                    street=address_dto.street,
                    house=address_dto.house,
                    address_type=address_dto.address_type.value,
                    apartment=address_dto.apartment,
                    entrance=address_dto.entrance,
                    floor=address_dto.floor,
                    intercom=address_dto.intercom,
                    is_primary=(idx == 0),
                    client_id=updated_client.client_id,
                )
                self._session.add(new_address)

    def next_id(self) -> ClientId:
        return ClientId(UUID(str(uuid7())))

    async def exists_with_number(self, number: str) -> bool:
        query = select(exists().where(ClientPhone.number == number))
        result = await self._session.execute(query)
        return bool(result.scalar())
