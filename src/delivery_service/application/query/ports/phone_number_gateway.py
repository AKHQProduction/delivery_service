from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from delivery_service.domain.customers.phone_number_id import PhoneNumberID


@dataclass(frozen=True)
class PhoneNumberReadModel:
    phone_number_id: PhoneNumberID
    number: str
    is_primary: bool


class PhoneNumberGateway(Protocol):
    @abstractmethod
    async def read_with_id(
        self, phone_number_id: PhoneNumberID
    ) -> PhoneNumberReadModel | None:
        raise NotImplementedError
