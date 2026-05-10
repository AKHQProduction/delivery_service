from dataclasses import dataclass

from backend.application.services.recurring.execution import (
    RecurringOrderExecution,
    RecurringOrderExecutionRequest,
)
from backend.application.vars import RecurringOrderStatus
from backend.infrastructure.persistence.gateways import (
    RecurringOrderFilters,
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class RunRecurringOrderAutomationCommand:
    pass


class RunRecurringOrderAutomationCommandHandler:
    def __init__(
        self,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        recurring_order_execution: RecurringOrderExecution,
        tr_manager: TransactionManager,
    ) -> None:
        self._recurring_order_gateway = recurring_order_gateway
        self._recurring_order_execution = recurring_order_execution
        self._tr_manager = tr_manager

    async def handle(self, _: RunRecurringOrderAutomationCommand) -> None:
        recurring_orders = await self._recurring_order_gateway.load_by_filters(
            RecurringOrderFilters(
                status=RecurringOrderStatus.ACTIVE,
                with_items=True,
            )
        )

        for recurring_order in recurring_orders:
            await self._recurring_order_execution.run(
                RecurringOrderExecutionRequest(
                    recurring_order_id=recurring_order.id,
                    shop_id=recurring_order.shop_id,
                    include_today=False,
                )
            )
            await self._tr_manager.commit()
