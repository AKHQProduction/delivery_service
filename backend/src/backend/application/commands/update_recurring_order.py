import logging
from dataclasses import dataclass

from backend.application.services.recurring.lifecycle import (
    RecurringOrderLifecycle,
)
from backend.application.services.recurring.management_context import (
    RecurringOrderManagementContext,
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
    ScheduleType,
    TimeSlotId,
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
        management_context: RecurringOrderManagementContext,
        template_write: RecurringOrderTemplateWritePolicy,
        recurring_order_lifecycle: RecurringOrderLifecycle,
        tr_manager: TransactionManager,
    ) -> None:
        self._management_context = management_context
        self._template_write = template_write
        self._recurring_order_lifecycle = recurring_order_lifecycle
        self._tr_manager = tr_manager

    async def handle(self, command: UpdateRecurringOrderCommand) -> None:
        current_user = await self._management_context.current_manager()
        recurring_order = await self._management_context.load_owned_with_items(
            command.recurring_order_id,
            current_user,
        )
        if command.rebuild_future_orders:
            self._recurring_order_lifecycle.ensure_can_rebuild_future_orders(
                recurring_order
            )

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

        if command.rebuild_future_orders:
            await self._recurring_order_lifecycle.rebuild_future_orders(
                recurring_order,
                current_user,
            )

        await self._tr_manager.commit()
        logger.info("Recurring order %s updated", recurring_order.id)
