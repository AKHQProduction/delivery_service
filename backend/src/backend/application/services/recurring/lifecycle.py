from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import (
    RecurringOrderPausedError,
    RecurringOrderTemplateInvalidError,
)
from backend.application.services.generated_order_lifecycle import (
    GeneratedOrderLifecycle,
)
from backend.application.services.recurring.execution import (
    RecurringOrderExecution,
    RecurringOrderExecutionRequest,
)
from backend.application.services.recurring.scheduling_clock import (
    RecurringOrderSchedulingClock,
)
from backend.application.services.recurring.template_integrity import (
    RecurringOrderTemplateIntegrity,
)
from backend.application.vars import RecurringOrderStatus
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)
from backend.infrastructure.transaction_manager import TransactionManager


class RecurringOrderLifecycle:
    def __init__(
        self,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        generated_order_lifecycle: GeneratedOrderLifecycle,
        recurring_order_execution: RecurringOrderExecution,
        scheduling_clock: RecurringOrderSchedulingClock,
        template_integrity: RecurringOrderTemplateIntegrity,
        tr_manager: TransactionManager,
    ) -> None:
        self._recurring_order_gateway = recurring_order_gateway
        self._generated_order_lifecycle = generated_order_lifecycle
        self._recurring_order_execution = recurring_order_execution
        self._scheduling_clock = scheduling_clock
        self._template_integrity = template_integrity
        self._tr_manager = tr_manager

    async def pause(
        self,
        recurring_order: RecurringOrder,
        current_user: CurrentUserDTO,
        *,
        cancel_future_orders: bool,
    ) -> None:
        recurring_order.status = RecurringOrderStatus.PAUSED
        if cancel_future_orders:
            await self._generated_order_lifecycle.delete_future_orders(
                recurring_order.id,
                self._scheduling_clock.future_order_cutoff(),
                current_user,
            )

    async def resume(self, recurring_order: RecurringOrder) -> None:
        if not await self._template_integrity.is_runnable(recurring_order):
            raise RecurringOrderTemplateInvalidError
        recurring_order.status = RecurringOrderStatus.ACTIVE

    async def delete(
        self,
        recurring_order: RecurringOrder,
        current_user: CurrentUserDTO,
        *,
        delete_future_orders: bool,
    ) -> None:
        if delete_future_orders:
            await self._generated_order_lifecycle.delete_future_orders(
                recurring_order.id,
                self._scheduling_clock.future_order_cutoff(),
                current_user,
            )
        await self._recurring_order_gateway.delete(recurring_order)

    def ensure_can_rebuild_future_orders(
        self, recurring_order: RecurringOrder
    ) -> None:
        if recurring_order.status == RecurringOrderStatus.PAUSED:
            raise RecurringOrderPausedError

    async def rebuild_future_orders(
        self,
        recurring_order: RecurringOrder,
        current_user: CurrentUserDTO,
    ) -> None:
        self.ensure_can_rebuild_future_orders(recurring_order)

        await self._generated_order_lifecycle.delete_future_orders_for_rebuild(
            recurring_order.id,
            self._scheduling_clock.future_order_cutoff(),
            current_user,
        )
        await self._tr_manager.flush()
        await self._recurring_order_execution.run(
            RecurringOrderExecutionRequest(
                recurring_order_id=recurring_order.id,
                shop_id=current_user.shop_id,
                include_today=False,
            )
        )
