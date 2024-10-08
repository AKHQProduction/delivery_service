from abc import abstractmethod
from asyncio import Protocol

from entities.shop.value_objects import ShopToken


class WebhookManager(Protocol):
    @abstractmethod
    async def setup_webhook(self, token: ShopToken) -> None:
        raise NotImplementedError

    @abstractmethod
    async def drop_webhook(self, token: ShopToken) -> None:
        raise NotImplementedError


class TokenVerifier(Protocol):
    @abstractmethod
    async def verify(self, token: str) -> None:
        raise NotImplementedError
