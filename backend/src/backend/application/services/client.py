from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.vars import ClientId, DistrictId, ShopId
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)


def create_client(
    *,
    client_id: ClientId,
    shop_id: ShopId,
    full_name: str,
) -> Client:
    return Client(id=client_id, shop_id=shop_id, full_name=full_name)


def update_client(
    client: Client,
    *,
    full_name: str | None = None,
) -> None:
    if full_name is not None:
        client.full_name = full_name


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
        address.latitude = coordinates.latitude
        address.longitude = coordinates.longitude
    if is_primary is not None:
        address.is_primary = is_primary
    if district_id is not None:
        address.district_id = district_id
