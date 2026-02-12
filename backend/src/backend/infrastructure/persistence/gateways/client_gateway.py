from sqlalchemy import (
    ColumnElement,
    asc,
    case,
    desc,
    exists,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils.compat import uuid7

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.client_gateway import (
    AddressDTO,
    ClientReadModel,
    DuplicatePhoneEntry,
    DuplicatePhoneOwner,
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
from backend.infrastructure.persistence.tables.shops import Shop
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyClientGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def save(self, entity: Client | ClientPhone | ClientAddress) -> None:
        self._session.add(entity)

    async def load(self, client_id: ClientId) -> Client | None:
        query = (
            select(Client)
            .where(Client.id == client_id)
            .options(
                selectinload(Client.phones),
                selectinload(Client.addresses).selectinload(
                    ClientAddress.district
                ),
            )
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, client: Client) -> None:
        await self._session.delete(client)

    async def read(self, client_id: ClientId) -> ClientReadModel | None:
        query = (
            select(Client)
            .where(Client.id == client_id)
            .options(
                selectinload(Client.phones),
                selectinload(Client.addresses),
            )
        )

        result = await self._session.execute(query)
        client = result.scalar_one_or_none()

        if client is None:
            return None

        return self._to_read_model(client)

    async def read_all(
        self,
        filters: GetClientsFilters,
        pagination: Pagination,
    ) -> list[ClientReadModel]:
        query = select(Client).options(
            selectinload(Client.phones),
            selectinload(Client.addresses),
        )

        if filters.shop_id:
            query = query.where(Client.shop_id == filters.shop_id)

        search_conditions: list[ColumnElement[bool]] = []
        if filters.full_name:
            search_conditions.append(
                Client.full_name.ilike(f"%{escape_like(filters.full_name)}%")
            )
        if filters.phone:
            phone_exists = exists(
                select(ClientPhone.id).where(
                    ClientPhone.client_id == Client.id,
                    ClientPhone.number.ilike(
                        f"%{escape_like(filters.phone)}%"
                    ),
                )
            )
            search_conditions.append(phone_exists)

        if search_conditions:
            query = query.where(or_(*search_conditions))

        ordering = []
        if filters.full_name:
            escaped = escape_like(filters.full_name)
            name_relevance = case(
                (func.lower(Client.full_name) == filters.full_name.lower(), 0),
                (Client.full_name.ilike(f"{escaped}%"), 1),
                else_=2,
            )
            ordering.append(asc(name_relevance))

        if pagination.order == SortOrder.ASC:
            ordering.extend([asc(Client.full_name), asc(Client.id)])
        else:
            ordering.extend([desc(Client.full_name), asc(Client.id)])

        query = query.order_by(*ordering)

        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        clients = result.scalars().all()

        return [self._to_read_model(client) for client in clients]

    @staticmethod
    def _to_read_model(client: Client) -> ClientReadModel:
        return ClientReadModel(
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
                    coordinates=CoordinatesDTO(
                        latitude=address.latitude,
                        longitude=address.longitude,
                    )
                    if address.latitude is not None
                    and address.longitude is not None
                    else None,
                    is_primary=address.is_primary,
                    id=AddressId(address.id),
                    district_id=address.district_id,
                )
                for address in client.addresses
            ],
        )

    async def find_coordinates_by_address(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        query = (
            select(
                ClientAddress.latitude,
                ClientAddress.longitude,
            )
            .join(Client, ClientAddress.client_id == Client.id)
            .join(Shop, Client.shop_id == Shop.id)
            .where(
                func.lower(func.btrim(ClientAddress.street))
                == street.strip().lower(),
                func.lower(func.btrim(ClientAddress.house))
                == house.strip().lower(),
                func.lower(func.btrim(Shop.city)) == city.strip().lower(),
                ClientAddress.latitude.isnot(None),
                ClientAddress.longitude.isnot(None),
            )
            .limit(1)
        )
        result = await self._session.execute(query)
        row = result.one_or_none()

        if row is None:
            return None

        return CoordinatesDTO(latitude=row.latitude, longitude=row.longitude)

    def next_id(self) -> ClientId:
        return ClientId(uuid7())

    async def find_duplicate_phones(
        self,
        shop_id: ShopId,
        phone_numbers: list[str],
        exclude_client_id: ClientId | None = None,
    ) -> list[DuplicatePhoneEntry]:
        if not phone_numbers:
            return []

        query = (
            select(
                ClientPhone.number,
                Client.id,
                Client.full_name,
            )
            .join(Client, ClientPhone.client_id == Client.id)
            .where(
                ClientPhone.shop_id == shop_id,
                ClientPhone.number.in_(phone_numbers),
            )
        )

        if exclude_client_id is not None:
            query = query.where(Client.id != exclude_client_id)

        result = await self._session.execute(query)

        grouped: dict[str, list[DuplicatePhoneOwner]] = {}
        for number, client_id, full_name in result.fetchall():
            grouped.setdefault(number, []).append(
                DuplicatePhoneOwner(
                    client_id=ClientId(client_id),
                    full_name=full_name,
                )
            )

        return [
            DuplicatePhoneEntry(phone_number=phone, owners=owners)
            for phone, owners in grouped.items()
        ]
