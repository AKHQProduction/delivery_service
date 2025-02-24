from abc import abstractmethod
from typing import Protocol

from delivery_service.core.users.user import UserID


class IDGenerator(Protocol):
    @abstractmethod
    def generate_service_client_id(self) -> UserID:
        raise NotImplementedError
