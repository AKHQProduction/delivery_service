from application.common.webhook_manager import WebhookManager
from entities.shop.value_objects import ShopToken


class FakeWebhookManager(WebhookManager):
    def __init__(self):
        self.setup = False
        self.dropped = False

    async def setup_webhook(self, token: ShopToken):
        self.setup = True

    async def drop_webhook(self, token: ShopToken):
        self.dropped = True
