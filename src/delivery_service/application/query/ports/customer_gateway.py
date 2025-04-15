from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from delivery_service.domain.customer_registries.customer_registry import (
    AddressData,
)
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID


@dataclass(frozen=True)
class CustomerReadModel:
    customer_id: UserID
    full_name: str
    primary_phone: str
    delivery_address: AddressData


@dataclass(frozen=True)
class CustomerGatewayFilters:
    shop_id: ShopID | None = None


class CustomerGateway(Protocol):
    @abstractmethod
    async def read_with_id(
        self, customer_id: UserID
    ) -> CustomerReadModel | None:
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
