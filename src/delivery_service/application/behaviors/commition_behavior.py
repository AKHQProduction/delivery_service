from typing import Any

from bazario import Request
from bazario.asyncio import HandleNext, PipelineBehavior

from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)


class CommitionBehavior(PipelineBehavior[Request, Any]):
    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._transaction_manager = transaction_manager

    async def handle(
        self,
        request: Request,
        handle_next: HandleNext[Request, Any],
    ) -> Any:
        handle_response = await handle_next(request)
        await self._transaction_manager.commit()

        return handle_response
