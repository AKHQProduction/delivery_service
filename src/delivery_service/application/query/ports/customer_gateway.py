from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from delivery_service.application.query.ports.address_gateway import (
    AddressReadModel,
)
from delivery_service.application.query.ports.phone_number_gateway import (
    PhoneNumberReadModel,
)
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.shared.shop_id import ShopID


@dataclass(frozen=True)
class CustomerReadModel:
    customer_id: CustomerID
    name: str
    addresses: list[AddressReadModel]
    phone_numbers: list[PhoneNumberReadModel]


@dataclass(frozen=True)
class CustomerGatewayFilters:
    shop_id: ShopID | None = None


class CustomerGateway(Protocol):
    @abstractmethod
    async def read_with_id(
        self, customer_id: CustomerID
    ) -> CustomerReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_with_phone(self, phone: str) -> CustomerReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_all_customers(
        self, filters: CustomerGatewayFilters | None = None
    ) -> Sequence[CustomerReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def total(
        self, filters: CustomerGatewayFilters | None = None
    ) -> int:
        raise NotImplementedError
