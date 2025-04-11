# ruff: noqa: E501
import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.dto import TelegramContactsData
from delivery_service.application.common.factories.service_user_factory import (
    ServiceUserFactory,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.application.ports.view_manager import (
    ViewManager,
)
from delivery_service.domain.user.repository import ServiceUserRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotStartRequest(TelegramRequest[None]):
    telegram_data: TelegramContactsData


class BotStartHandler(RequestHandler[BotStartRequest, None]):
    def __init__(
        self,
        service_user_repository: ServiceUserRepository,
        service_user_factory: ServiceUserFactory,
        view_manager: ViewManager,
        idp: IdentityProvider,
        transaction_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._repository = service_user_repository
        self._factory = service_user_factory
        self._view_manager = view_manager
        self._transaction_manager = transaction_manager

    async def handle(self, request: BotStartRequest) -> None:
        logger.info("Request from start bot")

        service_user = await self._repository.load_with_social_network(
            request.telegram_data.telegram_id
        )
        if not service_user:
            service_user = await self._factory.create_service_user(
                telegram_contacts=request.telegram_data,
            )
            self._repository.add(service_user)
            await self._transaction_manager.commit()

        await self._view_manager.send_greeting_message(
            user_id=service_user.entity_id
        )
