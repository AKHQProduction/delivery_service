from abc import abstractmethod
from typing import Protocol

from delivery_service.core.users.user import UserID


class IDGenerator(Protocol):
    @abstractmethod
    def generate_user_id(self) -> UserID:
        raise NotImplementedError
