from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.user_id import UserID


class ViewManager(Protocol):
    @abstractmethod
    async def send_greeting_message(self, user_id: UserID) -> None:
        raise NotImplementedError
