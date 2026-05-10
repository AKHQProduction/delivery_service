from dataclasses import dataclass

from backend.application.services.generated_order_lifecycle import (
    GeneratedOrderLifecycle,
)
from backend.application.services.recurring.management_context import (
    RecurringOrderManagementContext,
)
from backend.application.services.recurring.scheduling_clock import (
    RecurringOrderSchedulingClock,
)
from backend.application.vars import RecurringOrderId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class DeleteRecurringOrderCommand:
    recurring_order_id: RecurringOrderId
    delete_future_orders: bool = False


class DeleteRecurringOrderCommandHandler:
    def __init__(
        self,
        management_context: RecurringOrderManagementContext,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        generated_order_lifecycle: GeneratedOrderLifecycle,
        scheduling_clock: RecurringOrderSchedulingClock,
        tr_manager: TransactionManager,
    ) -> None:
        self._management_context = management_context
        self._recurring_order_gateway = recurring_order_gateway
        self._generated_order_lifecycle = generated_order_lifecycle
        self._scheduling_clock = scheduling_clock
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteRecurringOrderCommand) -> None:
        current_user = await self._management_context.current_manager()
        recurring_order = await self._management_context.load_owned(
            command.recurring_order_id,
            current_user,
        )
        if command.delete_future_orders:
            await self._generated_order_lifecycle.delete_future_orders(
                recurring_order.id,
                self._scheduling_clock.future_order_cutoff(),
                current_user,
            )
        await self._recurring_order_gateway.delete(recurring_order)
        await self._tr_manager.commit()
