from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.customers.customer import Customer


class CustomerRepository(Protocol):
    @abstractmethod
    def add(self, customer: Customer) -> None:
        raise NotImplementedError
