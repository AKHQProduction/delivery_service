import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.errors import (
    AccessDeniedError,
    RecurringOrderPausedError,
)
from backend.application.policies.access import ensure_can_manage
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
from backend.application.services.recurring.template_write import (
    RecurringOrderProductInput,
    RecurringOrderTemplateDraft,
    RecurringOrderTemplateWritePolicy,
)
from backend.application.vars import (
    AddressId,
    PhoneId,
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    TimeSlotId,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateRecurringOrderCommand:
    recurring_order_id: RecurringOrderId
    address_id: AddressId
    phone_id: PhoneId
    time_slot_id: TimeSlotId
    items: list[RecurringOrderProductInput]
    payment_method: str
    schedule_type: ScheduleType
    weekdays: list[int] | None = None
    month_days: list[int] | None = None
    comment: str | None = None
    rebuild_future_orders: bool = False


class UpdateRecurringOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        template_write: RecurringOrderTemplateWritePolicy,
        recurring_order_execution: RecurringOrderExecution,
        generated_order_lifecycle: GeneratedOrderLifecycle,
        scheduling_clock: RecurringOrderSchedulingClock,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._recurring_order_gateway = recurring_order_gateway
        self._template_write = template_write
        self._recurring_order_execution = recurring_order_execution
        self._generated_order_lifecycle = generated_order_lifecycle
        self._scheduling_clock = scheduling_clock
        self._tr_manager = tr_manager

    async def handle(self, command: UpdateRecurringOrderCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        recurring_order = ensure_exists(
            await self._recurring_order_gateway.load_with_items(
                command.recurring_order_id
            ),
            "RecurringOrder",
        )
        if recurring_order.shop_id != current_user.shop_id:
            raise AccessDeniedError
        if (
            command.rebuild_future_orders
            and recurring_order.status == RecurringOrderStatus.PAUSED
        ):
            raise RecurringOrderPausedError

        await self._template_write.apply(
            recurring_order,
            shop_id=current_user.shop_id,
            draft=RecurringOrderTemplateDraft(
                client_id=recurring_order.client_id,
                address_id=command.address_id,
                phone_id=command.phone_id,
                time_slot_id=command.time_slot_id,
                items=command.items,
                payment_method=command.payment_method,
                schedule_type=command.schedule_type,
                weekdays=command.weekdays,
                month_days=command.month_days,
                comment=command.comment,
            ),
        )

        if (
            recurring_order.status == RecurringOrderStatus.ACTIVE
            and command.rebuild_future_orders
        ):
            lifecycle = self._generated_order_lifecycle
            await lifecycle.delete_future_orders_for_rebuild(
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

        await self._tr_manager.commit()
        logger.info("Recurring order %s updated", recurring_order.id)
