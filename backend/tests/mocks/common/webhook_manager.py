from application.common.webhook_manager import WebhookManager


class FakeWebhookManager(WebhookManager):
    def __init__(self):
        self.setup = False
        self.dropped = False

    async def setup_webhook(self, token: str):
        self.setup = True

    async def drop_webhook(self, token: str):
        self.dropped = True
