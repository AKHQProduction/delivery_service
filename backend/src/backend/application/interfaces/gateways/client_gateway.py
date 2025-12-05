from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.interfaces.gateways import Pagination
from backend.application.vars import AddressType, ClientId, ShopId


@dataclass(frozen=True)
class PhoneDTO:
    number: str
    is_primary: bool = False


@dataclass(frozen=True)
class AddressDTO:
    street: str
    house: str
    address_type: AddressType
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    is_primary: bool = False


@dataclass(frozen=True)
class CreateClientDTO:
    client_id: ClientId
    shop_id: ShopId
    full_name: str
    phones: list[PhoneDTO]
    addresses: list[AddressDTO]
    custom_id: str | None = None


@dataclass
class ClientDM:  # Like entity
    client_id: ClientId
    shop_id: ShopId
    full_name: str
    phones: list[PhoneDTO]
    addresses: list[AddressDTO]
    custom_id: str | None = None


@dataclass(frozen=True)
class ClientReadModel:
    client_id: ClientId
    full_name: str
    phones: list[PhoneDTO]
    addresses: list[AddressDTO]
    custom_id: str | None = None


@dataclass(frozen=True)
class GetClientsFilters:
    shop_id: ShopId | None = None
    full_name: str | None = None
    custom_id: str | None = None
    phone: str | None = None


class ClientGateway(Protocol):
    @abstractmethod
    async def create_client(self, dto: CreateClientDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, client_id: ClientId) -> ClientDM | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, client_id: ClientId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, updated_client: ClientDM) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists_with_number(self, number: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def read(self, client_id: ClientId) -> ClientReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_all(
        self, filters: GetClientsFilters, pagination: Pagination
    ) -> list[ClientReadModel]:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> ClientId:
        raise NotImplementedError
