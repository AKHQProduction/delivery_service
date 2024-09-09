from abc import abstractmethod
from asyncio import Protocol


class WebhookManager(Protocol):
    @abstractmethod
    async def setup_webhook(self, token: str):
        raise NotImplementedError

    @abstractmethod
    async def drop_webhook(self, token: str):
        raise NotImplementedError
