from asyncio import Protocol


class WebhookManager(Protocol):
    async def setup_webhook(self, token: str):
        raise NotImplementedError
