from abc import abstractmethod
from typing import Protocol

from delivery_service.shared.domain.identity_id import UserID


class UserIDGenerator(Protocol):
    @abstractmethod
    def generate_user_id(self) -> UserID:
        raise NotImplementedError
