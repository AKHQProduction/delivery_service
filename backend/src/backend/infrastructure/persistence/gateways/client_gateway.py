from uuid import UUID

from sqlalchemy import asc, desc, or_, select
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
from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    ShopId,
)
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
                comment=address.comment,
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
            PhoneDTO(
                number=phone.number,
                is_primary=phone.is_primary,
                id=PhoneId(phone.id),
            )
            for phone in client.phones
        ]

        addresses = [
            AddressDTO(
                street=address.street,
                house=address.house,
                comment=address.comment,
                apartment=address.apartment,
                entrance=address.entrance,
                floor=address.floor,
                intercom=address.intercom,
                is_primary=address.is_primary,
                id=AddressId(address.id),
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
            PhoneDTO(
                number=phone.number,
                is_primary=phone.is_primary,
                id=PhoneId(phone.id),
            )
            for phone in client.phones
        ]

        addresses = [
            AddressDTO(
                street=address.street,
                house=address.house,
                comment=address.comment,
                apartment=address.apartment,
                entrance=address.entrance,
                floor=address.floor,
                intercom=address.intercom,
                is_primary=address.is_primary,
                id=AddressId(address.id),
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

        search_conditions = []
        if filters.full_name:
            search_conditions.append(
                Client.full_name.ilike(f"%{filters.full_name}%")
            )
        if filters.custom_id:
            search_conditions.append(
                Client.custom_id.ilike(f"%{filters.custom_id}%")
            )
        if filters.phone:
            query = query.outerjoin(ClientPhone)
            search_conditions.append(
                ClientPhone.number.ilike(f"%{filters.phone}%")
            )

        if search_conditions:
            query = query.where(or_(*search_conditions))

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
                    PhoneDTO(
                        number=phone.number,
                        is_primary=phone.is_primary,
                        id=PhoneId(phone.id),
                    )
                    for phone in client.phones
                ],
                addresses=[
                    AddressDTO(
                        street=address.street,
                        house=address.house,
                        comment=address.comment,
                        apartment=address.apartment,
                        entrance=address.entrance,
                        floor=address.floor,
                        intercom=address.intercom,
                        is_primary=address.is_primary,
                        id=AddressId(address.id),
                    )
                    for address in client.addresses
                ],
                custom_id=client.custom_id,
            )
            for client in clients
        ]

    async def update(self, updated_client: ClientDM) -> None:
        query = (
            select(Client)
            .where(Client.id == updated_client.client_id)
            .options(
                selectinload(Client.phones), selectinload(Client.addresses)
            )
        )
        result = await self._session.execute(query)
        client = result.scalar_one_or_none()

        if not client:
            return

        client.custom_id = updated_client.custom_id
        client.full_name = updated_client.full_name

        existing_phones_by_id = {phone.id: phone for phone in client.phones}
        updated_phone_ids = {
            phone_dto.id for phone_dto in updated_client.phones if phone_dto.id
        }

        for phone_dto in updated_client.phones:
            if phone_dto.id and phone_dto.id in existing_phones_by_id:
                existing_phone = existing_phones_by_id[phone_dto.id]
                existing_phone.number = phone_dto.number
                existing_phone.is_primary = phone_dto.is_primary
            else:
                new_phone = ClientPhone(
                    number=phone_dto.number,
                    is_primary=phone_dto.is_primary,
                    client_id=updated_client.client_id,
                    shop_id=updated_client.shop_id,
                )
                self._session.add(new_phone)

        for phone_id, phone in existing_phones_by_id.items():
            if phone_id not in updated_phone_ids:
                await self._session.delete(phone)

        existing_addresses_by_id = {
            address.id: address for address in client.addresses
        }
        updated_address_ids = {
            addr_dto.id for addr_dto in updated_client.addresses if addr_dto.id
        }

        for address_dto in updated_client.addresses:
            if address_dto.id and address_dto.id in existing_addresses_by_id:
                existing_address = existing_addresses_by_id[address_dto.id]
                existing_address.street = address_dto.street
                existing_address.house = address_dto.house
                existing_address.comment = address_dto.comment
                existing_address.apartment = address_dto.apartment
                existing_address.entrance = address_dto.entrance
                existing_address.floor = address_dto.floor
                existing_address.intercom = address_dto.intercom
                existing_address.is_primary = address_dto.is_primary
            else:
                new_address = ClientAddress(
                    street=address_dto.street,
                    house=address_dto.house,
                    comment=address_dto.comment,
                    apartment=address_dto.apartment,
                    entrance=address_dto.entrance,
                    floor=address_dto.floor,
                    intercom=address_dto.intercom,
                    is_primary=address_dto.is_primary,
                    client_id=updated_client.client_id,
                )
                self._session.add(new_address)

        for address_id, address in existing_addresses_by_id.items():
            if address_id not in updated_address_ids:
                await self._session.delete(address)

    def next_id(self) -> ClientId:
        return ClientId(UUID(str(uuid7())))

    async def check_existing_numbers(self, numbers: list[str]) -> set[str]:
        if not numbers:
            return set()

        query = select(ClientPhone.number).where(
            ClientPhone.number.in_(numbers)
        )
        result = await self._session.execute(query)

        return {row[0] for row in result.fetchall()}
