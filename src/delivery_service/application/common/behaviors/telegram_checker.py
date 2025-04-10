from typing import Any, Generic

from bazario.asyncio import HandleNext, PipelineBehavior
from typing_extensions import TypeVar

from delivery_service.application.common.behaviors.base import BehaviorResult
from delivery_service.application.common.errors import AuthenticationError
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.ports.social_network_checker import (
    SocialNetworkChecker,
)
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.domain.user.repository import ServiceUserRepository

CheckerAllowableRequests = TypeVar(
    "CheckerAllowableRequests", bound=TelegramRequest
)


class TelegramCheckerBehavior(
    PipelineBehavior[CheckerAllowableRequests, BehaviorResult],
    Generic[CheckerAllowableRequests, BehaviorResult],
):
    def __init__(
        self,
        service_user_repository: ServiceUserRepository,
        idp: IdentityProvider,
        social_network_checker: SocialNetworkChecker,
        transaction_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._service_user_repository = service_user_repository
        self._social_network_checker = social_network_checker
        self._transaction_manager = transaction_manager

    async def handle(
        self,
        request: CheckerAllowableRequests,
        handle_next: HandleNext[CheckerAllowableRequests, BehaviorResult],
    ) -> Any:
        try:
            current_user_id = await self._idp.get_current_user_id()
        except AuthenticationError:
            return await handle_next(request)

        service_user = await self._service_user_repository.load_by_identity(
            current_user_id
        )
        if not service_user:
            return await handle_next(request)

        telegram_contacts = service_user.telegram_contacts
        telegram_data = await self._social_network_checker.check_telegram_data(
            telegram_contacts.telegram_id
        )

        if telegram_data:
            if (
                telegram_data.telegram_username
                != telegram_contacts.telegram_username
            ):
                service_user.edit_telegram_contacts(
                    telegram_id=None,
                    telegram_username=telegram_data.telegram_username,
                )
            if telegram_data.full_name != service_user.full_name:
                service_user.edit_full_name(telegram_data.full_name)

            if telegram_data.full_name != service_user.full_name:
                service_user.edit_full_name(telegram_data.full_name)
        return await handle_next(request)
