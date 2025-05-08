from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, Sequence

from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.customers.customer_id import CustomerID


@dataclass(frozen=True)
class AddressReadModel:
    address_id: AddressID
    city: str
    street: str
    house_number: str
    apartment_number: str | None
    floor: int | None
    intercom_code: str | None

    @property
    def full_address(self) -> str:
        return f"{self.city}, {self.street} {self.house_number}"


@dataclass(frozen=True)
class AddressGatewayFilters:
    customer_id: CustomerID | None = None


class AddressGateway(Protocol):
    @abstractmethod
    async def read_many(
        self, filters: AddressGatewayFilters | None = None
    ) -> Sequence[AddressReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def read_with_id(
        self, address_id: AddressID
    ) -> AddressReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def total(self, filters: AddressGatewayFilters | None = None) -> int:
        raise NotImplementedError
