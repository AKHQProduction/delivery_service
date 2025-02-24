from abc import abstractmethod
from typing import Protocol


class ViewManager(Protocol):
    @abstractmethod
    async def send_greeting_message(self) -> None:
        raise NotImplementedError
