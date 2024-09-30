from abc import abstractmethod
from asyncio import Protocol

from entities.shop.value_objects import ShopToken


class WebhookManager(Protocol):
    @abstractmethod
    async def setup_webhook(self, token: ShopToken):
        raise NotImplementedError

    @abstractmethod
    async def drop_webhook(self, token: ShopToken):
        raise NotImplementedError
