from abc import abstractmethod
from typing import Protocol


class SocialNetworkProvider(Protocol):
    @abstractmethod
    async def get_telegram_id(self) -> int | None:
        raise NotImplementedError
