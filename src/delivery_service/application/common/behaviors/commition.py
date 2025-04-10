from typing import Any, Generic, TypeVar

from bazario.asyncio import HandleNext, PipelineBehavior

from delivery_service.application.common.behaviors.base import BehaviorResult
from delivery_service.application.common.markers.requests import (
    BaseCommand,
)
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)

AllowableRequests = TypeVar("AllowableRequests", bound=BaseCommand)


class CommitionBehavior(
    PipelineBehavior[AllowableRequests, BehaviorResult],
    Generic[AllowableRequests, BehaviorResult],
):
    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._transaction_manager = transaction_manager

    async def handle(
        self,
        request: AllowableRequests,
        handle_next: HandleNext[AllowableRequests, BehaviorResult],
    ) -> Any:
        handle_response = await handle_next(request)
        await self._transaction_manager.commit()

        return handle_response
