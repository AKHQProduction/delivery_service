from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.shared.user_id import UserID


class CustomerRepository(Protocol):
    @abstractmethod
    def add(self, customer: Customer) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_id(self, customer_id: UserID) -> Customer | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, customer: Customer) -> None:
        raise NotImplementedError
