from typing import Any, Generic

from bazario.asyncio import HandleNext, PipelineBehavior
from typing_extensions import TypeVar

from delivery_service.application.common.behaviors.base import BehaviorResult
from delivery_service.application.common.markers.command import TelegramCommand
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.ports.social_network_checker import (
    SocialNetworkChecker,
)
from delivery_service.domain.user.repository import ServiceUserRepository

CheckerAllowableCommands = TypeVar(
    "CheckerAllowableCommands", bound=TelegramCommand
)


class TelegramCheckerBehavior(
    PipelineBehavior[CheckerAllowableCommands, BehaviorResult],
    Generic[CheckerAllowableCommands, BehaviorResult],
):
    def __init__(
        self,
        service_user_repository: ServiceUserRepository,
        idp: IdentityProvider,
        social_network_checker: SocialNetworkChecker,
    ) -> None:
        self._idp = idp
        self._service_user_repository = service_user_repository
        self._social_network_checker = social_network_checker

    async def handle(
        self,
        request: CheckerAllowableCommands,
        handle_next: HandleNext[CheckerAllowableCommands, BehaviorResult],
    ) -> Any:
        current_user_id = await self._idp.get_current_user_id()

        service_user = await self._service_user_repository.load_by_identity(
            current_user_id
        )
        if not service_user:
            return await handle_next(request)

        if (
            telegram_data
            := await self._social_network_checker.check_telegram_data(
                service_user.telegram_contacts.telegram_id
            )
        ):
            if (
                telegram_data.telegram_username
                != service_user.telegram_contacts.telegram_username
            ):
                service_user.edit_telegram_contacts(
                    telegram_id=None,
                    telegram_username=telegram_data.telegram_username,
                )
            if telegram_data.full_name != service_user.full_name:
                service_user.edit_full_name(telegram_data.full_name)

        return await handle_next(request)
