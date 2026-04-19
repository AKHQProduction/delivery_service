from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PhoneSchema(BaseModel):
    number: str
    is_primary: bool = False
    id: int | None = None


class CoordinatesSchema(BaseModel):
    latitude: float
    longitude: float


class AddressSchema(BaseModel):
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None
    coordinates: CoordinatesSchema | None = None
    is_primary: bool = False
    id: int | None = None
    district_id: UUID | None = None


class EditClientSchema(BaseModel):
    full_name: str | None = None
    balance: Decimal | None = Field(
        default=None, max_digits=10, decimal_places=2
    )
    phones: list[PhoneSchema] | None = None
    addresses: list[AddressSchema] | None = None
    confirm_duplicate_phones: bool = False


class SetClientBalanceSchema(BaseModel):
    balance: Decimal = Field(max_digits=10, decimal_places=2)
