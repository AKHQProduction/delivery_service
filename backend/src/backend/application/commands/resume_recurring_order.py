from dataclasses import dataclass

from backend.application.errors import RecurringOrderTemplateInvalidError
from backend.application.services.recurring_order_management_context import (
    RecurringOrderManagementContext,
)
from backend.application.services.recurring_order_template_integrity import (
    RecurringOrderTemplateIntegrity,
)
from backend.application.vars import RecurringOrderId, RecurringOrderStatus
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class ResumeRecurringOrderCommand:
    recurring_order_id: RecurringOrderId


class ResumeRecurringOrderCommandHandler:
    def __init__(
        self,
        management_context: RecurringOrderManagementContext,
        template_integrity: RecurringOrderTemplateIntegrity,
        tr_manager: TransactionManager,
    ) -> None:
        self._management_context = management_context
        self._template_integrity = template_integrity
        self._tr_manager = tr_manager

    async def handle(self, command: ResumeRecurringOrderCommand) -> None:
        current_user = await self._management_context.current_manager()
        recurring_order = await self._management_context.load_owned_with_items(
            command.recurring_order_id,
            current_user,
        )
        if not await self._template_integrity.is_runnable(recurring_order):
            raise RecurringOrderTemplateInvalidError
        recurring_order.status = RecurringOrderStatus.ACTIVE
        await self._tr_manager.commit()
