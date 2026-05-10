from dataclasses import dataclass

from backend.application.services.recurring.lifecycle import (
    RecurringOrderLifecycle,
)
from backend.application.services.recurring.management_context import (
    RecurringOrderManagementContext,
)
from backend.application.vars import RecurringOrderId
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class DeleteRecurringOrderCommand:
    recurring_order_id: RecurringOrderId
    delete_future_orders: bool = False


class DeleteRecurringOrderCommandHandler:
    def __init__(
        self,
        management_context: RecurringOrderManagementContext,
        recurring_order_lifecycle: RecurringOrderLifecycle,
        tr_manager: TransactionManager,
    ) -> None:
        self._management_context = management_context
        self._recurring_order_lifecycle = recurring_order_lifecycle
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteRecurringOrderCommand) -> None:
        current_user = await self._management_context.current_manager()
        recurring_order = await self._management_context.load_owned(
            command.recurring_order_id,
            current_user,
        )
        await self._recurring_order_lifecycle.delete(
            recurring_order,
            current_user,
            delete_future_orders=command.delete_future_orders,
        )
        await self._tr_manager.commit()
