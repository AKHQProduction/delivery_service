from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.customer_registries.customer_registry import (
    CustomerRegistry,
)
from delivery_service.domain.shared.user_id import UserID


class CustomerRegistryRepository(Protocol):
    @abstractmethod
    async def load_with_identity(
        self, identity_id: UserID
    ) -> CustomerRegistry | None:
        raise NotImplementedError
