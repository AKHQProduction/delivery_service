from dataclasses import dataclass

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    PhoneId,
    ShopId,
)


@dataclass(frozen=True)
class PhoneDTO:
    number: str
    is_primary: bool = False
    id: PhoneId | None = None


@dataclass(frozen=True)
class AddressDTO:
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None
    coordinates: CoordinatesDTO | None = None
    is_primary: bool = False
    id: AddressId | None = None
    district_id: DistrictId | None = None


@dataclass(frozen=True)
class ClientReadModel:
    client_id: ClientId
    full_name: str
    phones: list[PhoneDTO]
    addresses: list[AddressDTO]


@dataclass(frozen=True)
class DuplicatePhoneOwner:
    client_id: ClientId
    full_name: str


@dataclass(frozen=True)
class DuplicatePhoneEntry:
    phone_number: str
    owners: list[DuplicatePhoneOwner]


@dataclass(frozen=True)
class GetClientsFilters:
    shop_id: ShopId | None = None
    full_name: str | None = None
    phone: str | None = None
