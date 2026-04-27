from dataclasses import dataclass
from decimal import Decimal

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.errors import (
    ExistingClientInfo,
    PhoneDuplicate,
    PhoneNumberAlreadyExistsError,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    Empty,
    PhoneId,
    ShopId,
    TimeSlotId,
)
from backend.infrastructure.persistence.gateways.client_gateway import (
    SQLAlchemyClientGateway,
)
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)


@dataclass(frozen=True)
class PhoneSyncItem:
    number: str
    is_primary: bool
    id: PhoneId | None = None


@dataclass(frozen=True)
class AddressSyncItem:
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None
    coordinates: CoordinatesDTO | None = None
    is_primary: bool = False
    district_id: DistrictId | None = None
    id: AddressId | None = None


def create_client(
    *,
    client_id: ClientId,
    shop_id: ShopId,
    full_name: str,
    preferred_time_slot_id: TimeSlotId | None = None,
) -> Client:
    return Client(
        id=client_id,
        shop_id=shop_id,
        full_name=full_name,
        preferred_time_slot_id=preferred_time_slot_id,
        balance=Decimal(0),
    )


def update_client(
    client: Client,
    *,
    full_name: str | None = None,
    balance: Decimal | None = None,
    preferred_time_slot_id: TimeSlotId | Empty | None = Empty.EMPTY,
) -> None:
    if full_name is not None:
        client.full_name = full_name
    if balance is not None:
        client.balance = balance
    if preferred_time_slot_id is not Empty.EMPTY:
        client.preferred_time_slot_id = (
            None
            if preferred_time_slot_id is None
            else TimeSlotId(preferred_time_slot_id)
        )


def set_client_balance(client: Client, *, balance: Decimal) -> None:
    client.balance = balance


def create_phone(
    *,
    number: str,
    is_primary: bool,
    shop_id: ShopId,
) -> ClientPhone:
    return ClientPhone(
        number=number,
        is_primary=is_primary,
        shop_id=shop_id,
    )


def update_phone(
    phone: ClientPhone,
    *,
    number: str | None = None,
    is_primary: bool | None = None,
) -> None:
    if number is not None:
        phone.number = number
    if is_primary is not None:
        phone.is_primary = is_primary


def create_address(
    *,
    street: str,
    house: str,
    apartment: str | None = None,
    entrance: str | None = None,
    floor: str | None = None,
    intercom: str | None = None,
    comment: str | None = None,
    coordinates: CoordinatesDTO | None = None,
    is_primary: bool = False,
    district_id: DistrictId | None = None,
) -> ClientAddress:
    return ClientAddress(
        street=street,
        house=house,
        apartment=apartment,
        entrance=entrance,
        floor=floor,
        intercom=intercom,
        comment=comment,
        latitude=coordinates.latitude if coordinates else None,
        longitude=coordinates.longitude if coordinates else None,
        is_primary=is_primary,
        district_id=district_id,
    )


def update_address(
    address: ClientAddress,
    *,
    street: str | None = None,
    house: str | None = None,
    apartment: str | None = None,
    entrance: str | None = None,
    floor: str | None = None,
    intercom: str | None = None,
    comment: str | None = None,
    coordinates: CoordinatesDTO | None = None,
    is_primary: bool | None = None,
    district_id: DistrictId | None = None,
) -> None:
    if street is not None:
        address.street = street
    if house is not None:
        address.house = house
    if apartment is not None:
        address.apartment = apartment
    if entrance is not None:
        address.entrance = entrance
    if floor is not None:
        address.floor = floor
    if intercom is not None:
        address.intercom = intercom
    if comment is not None:
        address.comment = comment
    if coordinates is not None:
        coordinates.apply_to(address)
    if is_primary is not None:
        address.is_primary = is_primary
    if district_id is not None:
        address.district_id = district_id


async def check_phone_duplicates(
    *,
    client_gateway: SQLAlchemyClientGateway,
    shop_id: ShopId,
    phone_numbers: list[str],
    exclude_client_id: ClientId | None = None,
) -> None:
    duplicates = await client_gateway.find_duplicate_phones(
        shop_id=shop_id,
        phone_numbers=phone_numbers,
        exclude_client_id=exclude_client_id,
    )
    if duplicates:
        raise PhoneNumberAlreadyExistsError(
            duplicates=[
                PhoneDuplicate(
                    phone_number=dup.phone_number,
                    existing_clients=[
                        ExistingClientInfo(
                            client_id=o.client_id,
                            full_name=o.full_name,
                        )
                        for o in dup.owners
                    ],
                )
                for dup in duplicates
            ]
        )


def sync_phones(
    client: Client,
    *,
    phones: list[PhoneSyncItem],
    shop_id: ShopId,
) -> None:
    existing = {p.id: p for p in client.phones}
    incoming_ids = {p.id for p in phones if p.id}

    for item in phones:
        if item.id and item.id in existing:
            update_phone(
                existing[item.id],
                number=item.number,
                is_primary=item.is_primary,
            )
        else:
            client.phones.append(
                create_phone(
                    number=item.number,
                    is_primary=item.is_primary,
                    shop_id=shop_id,
                )
            )

    for phone_id, phone in existing.items():
        if phone_id not in incoming_ids:
            client.phones.remove(phone)


def sync_addresses(
    client: Client,
    *,
    addresses: list[AddressSyncItem],
) -> None:
    existing = {a.id: a for a in client.addresses}
    incoming_ids = {a.id for a in addresses if a.id}

    for item in addresses:
        if item.id and item.id in existing:
            update_address(
                existing[item.id],
                street=item.street,
                house=item.house,
                apartment=item.apartment,
                entrance=item.entrance,
                floor=item.floor,
                intercom=item.intercom,
                comment=item.comment,
                coordinates=item.coordinates,
                is_primary=item.is_primary,
                district_id=item.district_id,
            )
        else:
            client.addresses.append(
                create_address(
                    street=item.street,
                    house=item.house,
                    apartment=item.apartment,
                    entrance=item.entrance,
                    floor=item.floor,
                    intercom=item.intercom,
                    comment=item.comment,
                    coordinates=item.coordinates,
                    is_primary=item.is_primary,
                    district_id=item.district_id,
                )
            )

    for addr_id, addr in existing.items():
        if addr_id not in incoming_ids:
            client.addresses.remove(addr)
