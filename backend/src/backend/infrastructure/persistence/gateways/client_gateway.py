from decimal import Decimal
from itertools import starmap
from typing import Any

from sqlalchemy import (
    ColumnElement,
    asc,
    case,
    desc,
    exists,
    func,
    insert,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils.compat import uuid7

from backend.application.dto.coordinates import (
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.client_gateway import (
    AddressDTO,
    ClientReadModel,
    DuplicatePhoneEntry,
    DuplicatePhoneOwner,
    GetClientsFilters,
    PhoneDTO,
)
from backend.application.validators import (
    HOUSE_LETTER_SQL_RE,
    HOUSE_LETTER_SQL_REPL,
    STREET_PREFIX_SQL_RE,
    normalize_house,
    normalize_street,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    ShopId,
    TimeSlotId,
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

    async def save_all(self, entities: list[Client]) -> None:
        if not entities:
            return

        client_rows: list[dict[str, Any]] = []
        phone_rows: list[dict[str, Any]] = []
        address_rows: list[dict[str, Any]] = []

        for client in entities:
            client_rows.append({
                "id": client.id,
                "shop_id": client.shop_id,
                "full_name": client.full_name,
                "user_id": client.user_id or None,
                "preferred_time_slot_id": client.preferred_time_slot_id,
                "balance": (
                    client.balance
                    if client.balance is not None
                    else Decimal(0)
                ),
            })
            phone_rows.extend(
                {
                    "number": phone.number,
                    "is_primary": phone.is_primary,
                    "client_id": client.id,
                    "shop_id": phone.shop_id,
                }
                for phone in client.phones
            )
            address_rows.extend(
                {
                    "street": addr.street,
                    "house": addr.house,
                    "apartment": addr.apartment,
                    "entrance": addr.entrance,
                    "floor": addr.floor,
                    "intercom": addr.intercom,
                    "comment": addr.comment,
                    "latitude": addr.latitude,
                    "longitude": addr.longitude,
                    "is_primary": addr.is_primary,
                    "client_id": client.id,
                    "district_id": addr.district_id,
                }
                for addr in client.addresses
            )

        await self._session.execute(insert(Client), client_rows)
        if phone_rows:
            await self._session.execute(insert(ClientPhone), phone_rows)
        if address_rows:
            await self._session.execute(insert(ClientAddress), address_rows)

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

    async def load_for_update(self, client_id: ClientId) -> Client | None:
        query = select(Client).where(Client.id == client_id).with_for_update()
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
            preferred_time_slot_id=TimeSlotId(client.preferred_time_slot_id)
            if client.preferred_time_slot_id is not None
            else None,
            balance=client.balance,
        )

    async def find_coordinates_by_address(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        norm_street_col = func.btrim(
            func.regexp_replace(
                func.lower(func.btrim(ClientAddress.street)),
                STREET_PREFIX_SQL_RE,
                "",
            )
        )
        filters = [
            norm_street_col == normalize_street(street),
            func.lower(func.btrim(Shop.city)) == city.strip().lower(),
            ClientAddress.latitude.isnot(None),
            ClientAddress.longitude.isnot(None),
        ]
        if house.strip():
            norm_house_col = func.regexp_replace(
                func.lower(func.btrim(ClientAddress.house)),
                HOUSE_LETTER_SQL_RE,
                HOUSE_LETTER_SQL_REPL,
                "g",
            )
            filters.append(norm_house_col == normalize_house(house))
        query = (
            select(
                ClientAddress.latitude,
                ClientAddress.longitude,
            )
            .join(Client, ClientAddress.client_id == Client.id)
            .join(Shop, Client.shop_id == Shop.id)
            .where(*filters)
            .limit(1)
        )
        result = await self._session.execute(query)
        row = result.one_or_none()

        if row is None:
            return None

        return CoordinatesDTO(latitude=row.latitude, longitude=row.longitude)

    async def find_address_by_coordinates(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        query = (
            select(
                ClientAddress.street,
                ClientAddress.house,
                Shop.city,
            )
            .join(Client, ClientAddress.client_id == Client.id)
            .join(Shop, Client.shop_id == Shop.id)
            .where(
                ClientAddress.latitude == coordinates.latitude,
                ClientAddress.longitude == coordinates.longitude,
            )
            .limit(1)
        )
        result = await self._session.execute(query)
        row = result.one_or_none()

        if row is None:
            return None

        parts = [p for p in (row.street, row.house, row.city) if p]
        return ReverseGeocodeResult(
            display_name=", ".join(parts),
            street=row.street,
            house=row.house,
            city=row.city,
            district=None,
        )

    def next_id(self) -> ClientId:
        return ClientId(uuid7())

    async def find_candidate_ids_for_dedup(
        self,
        shop_id: ShopId,
        phone_numbers: set[str],
        addresses: set[tuple[str, str]],
    ) -> set[ClientId]:
        candidate_ids: set[ClientId] = set()

        if phone_numbers:
            phone_query = select(ClientPhone.client_id).where(
                ClientPhone.shop_id == shop_id,
                ClientPhone.number.in_(phone_numbers),
            )
            result = await self._session.execute(phone_query)
            candidate_ids.update(starmap(ClientId, result.fetchall()))

        if addresses:
            addr_tuples = list(starmap(func.row, addresses))
            norm_street_col = func.btrim(
                func.regexp_replace(
                    func.lower(func.btrim(ClientAddress.street)),
                    STREET_PREFIX_SQL_RE,
                    "",
                )
            )
            norm_house_col = func.regexp_replace(
                func.lower(func.btrim(ClientAddress.house)),
                HOUSE_LETTER_SQL_RE,
                HOUSE_LETTER_SQL_REPL,
                "g",
            )
            addr_query = (
                select(ClientAddress.client_id)
                .join(Client, ClientAddress.client_id == Client.id)
                .where(
                    Client.shop_id == shop_id,
                    func.row(
                        norm_street_col,
                        norm_house_col,
                    ).in_(addr_tuples),
                )
            )
            result = await self._session.execute(addr_query)
            candidate_ids.update(starmap(ClientId, result.fetchall()))

        return candidate_ids

    async def load_candidates_for_dedup(
        self,
        client_ids: set[ClientId],
    ) -> list[Client]:
        if not client_ids:
            return []

        query = (
            select(Client)
            .where(Client.id.in_(client_ids))
            .options(
                selectinload(Client.phones),
                selectinload(Client.addresses),
            )
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

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
