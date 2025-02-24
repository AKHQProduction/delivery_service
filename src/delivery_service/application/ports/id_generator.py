from abc import abstractmethod
from typing import Protocol

from delivery_service.core.users.service_client import ServiceClientID


class IDGenerator(Protocol):
    @abstractmethod
    def generate_service_client_id(self) -> ServiceClientID:
        raise NotImplementedError
