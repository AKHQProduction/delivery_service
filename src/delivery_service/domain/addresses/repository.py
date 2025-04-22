from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.addresses.address import Address
from delivery_service.domain.addresses.address_id import AddressID


class AddressRepository(Protocol):
    @abstractmethod
    async def load_with_id(self, address_id: AddressID) -> Address | None:
        raise NotImplementedError
