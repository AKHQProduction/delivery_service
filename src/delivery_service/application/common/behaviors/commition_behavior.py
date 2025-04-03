from typing import Any, Generic, TypeVar

from bazario.asyncio import HandleNext, PipelineBehavior

from delivery_service.application.common.behaviors.base import BehaviorResult
from delivery_service.application.common.markers.command import (
    Command,
)
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)

AllowableCommands = TypeVar("AllowableCommands", bound=Command)


class CommitionBehavior(
    PipelineBehavior[AllowableCommands, BehaviorResult],
    Generic[AllowableCommands, BehaviorResult],
):
    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._transaction_manager = transaction_manager

    async def handle(
        self,
        request: AllowableCommands,
        handle_next: HandleNext[AllowableCommands, BehaviorResult],
    ) -> Any:
        handle_response = await handle_next(request)
        await self._transaction_manager.commit()

        return handle_response
