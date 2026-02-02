from pydantic import BaseModel


class PhoneSchema(BaseModel):
    number: str
    is_primary: bool = False
    id: int | None = None


class AddressSchema(BaseModel):
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None
    is_primary: bool = False
    id: int | None = None


class EditClientSchema(BaseModel):
    full_name: str | None = None
    phones: list[PhoneSchema] | None = None
    addresses: list[AddressSchema] | None = None
    confirm_duplicate_phones: bool = False
