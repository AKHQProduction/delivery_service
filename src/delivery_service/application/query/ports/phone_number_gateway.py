from dataclasses import dataclass

from delivery_service.domain.customers.phone_number_id import PhoneNumberID


@dataclass(frozen=True)
class PhoneNumberReadModel:
    phone_number_id: PhoneNumberID
    number: str
    is_primary: bool
