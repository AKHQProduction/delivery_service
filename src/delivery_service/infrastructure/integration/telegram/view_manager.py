import logging

from delivery_service.application.ports.view_manager import ViewManager


class TelegramViewManager(ViewManager):
    async def send_greeting_message(self) -> None:
        logging.info("Hello")
