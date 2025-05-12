# ruff: noqa: E501
from typing import Any, Generic

from bazario.asyncio import HandleNext, PipelineBehavior
from typing_extensions import TypeVar

from delivery_service.application.common.behaviors.base import BehaviorResult
from delivery_service.application.common.factories.service_user_factory import (
    ServiceUserFactory,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.social_network_checker import (
    SocialNetworkChecker,
)
from delivery_service.application.ports.social_network_provider import (
    SocialNetworkProvider,
)
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.domain.shared.new_types import Empty
from delivery_service.domain.users.repository import ServiceUserRepository

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
        service_user_factory: ServiceUserFactory,
        social_network_provider: SocialNetworkProvider,
        social_network_checker: SocialNetworkChecker,
        transaction_manager: TransactionManager,
    ) -> None:
        self._service_user_repository = service_user_repository
        self._service_user_factory = service_user_factory
        self._social_network_provider = social_network_provider
        self._social_network_checker = social_network_checker
        self._transaction_manager = transaction_manager

    async def handle(
        self,
        request: CheckerAllowableRequests,
        handle_next: HandleNext[CheckerAllowableRequests, BehaviorResult],
    ) -> Any:
        telegram_id = await self._social_network_provider.get_telegram_id()
        if not telegram_id:
            return await handle_next(request)

        service_user = (
            await self._service_user_repository.load_with_social_network(
                telegram_id
            )
        )
        if service_user is None:
            telegram_data = (
                await self._social_network_checker.check_telegram_data(
                    telegram_id
                )
            )
            if telegram_data:
                service_user = (
                    await self._service_user_factory.create_service_user(
                        telegram_data
                    )
                )
                self._service_user_repository.add(service_user)
                await self._transaction_manager.commit()
            return await handle_next(request)

        telegram_contacts = service_user.telegram_contacts
        telegram_data = await self._social_network_checker.check_telegram_data(
            telegram_contacts.telegram_id
        )

        if telegram_data:
            updated = False

            if (
                telegram_data.telegram_username == Empty.UNSET
                and telegram_contacts.telegram_username is not None
            ) or (
                telegram_data.telegram_username != Empty.UNSET
                and telegram_contacts.telegram_username is None
            ):
                service_user.edit_telegram_contacts(
                    telegram_id=None,
                    telegram_username=telegram_data.telegram_username,
                )
                updated = True

            if telegram_data.full_name != service_user.full_name:
                service_user.edit_full_name(telegram_data.full_name)
                updated = True

            if updated:
                await self._transaction_manager.commit()

        return await handle_next(request)
