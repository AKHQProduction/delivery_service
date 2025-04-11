# ruff: noqa: E501
import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.ports.view_manager import (
    ViewManager,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotStartRequest(TelegramRequest[None]):
    pass


class BotStartHandler(RequestHandler[BotStartRequest, None]):
    def __init__(
        self, idp: IdentityProvider, view_manager: ViewManager
    ) -> None:
        self._idp = idp
        self._view_manager = view_manager

    async def handle(self, request: BotStartRequest) -> None:
        logger.info("Request from start bot")
        current_user_id = await self._idp.get_current_user_id()

        await self._view_manager.send_greeting_message(user_id=current_user_id)
