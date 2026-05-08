from dataclasses import dataclass
from datetime import date

from backend.application.policies.access import ensure_can_manage
from backend.application.services.recurring_order_execution import (
    RecurringOrderExecution,
    RecurringOrderExecutionRequest,
)
from backend.application.vars import RecurringOrderId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class RunRecurringOrderCommand:
    recurring_order_id: RecurringOrderId
    include_today: bool = False
    activate: bool = False


@dataclass(frozen=True)
class RunRecurringOrderResult:
    created_dates: list[date]
    already_scheduled_dates: list[date]
    cancelled_dates: list[date]
    paused: bool


class RunRecurringOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_execution: RecurringOrderExecution,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._recurring_order_execution = recurring_order_execution
        self._tr_manager = tr_manager

    async def handle(
        self, command: RunRecurringOrderCommand
    ) -> RunRecurringOrderResult:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        result = await self._recurring_order_execution.run(
            RecurringOrderExecutionRequest(
                recurring_order_id=command.recurring_order_id,
                shop_id=current_user.shop_id,
                include_today=command.include_today,
                activate=command.activate,
            )
        )
        await self._tr_manager.commit()
        return RunRecurringOrderResult(
            created_dates=result.created_dates,
            already_scheduled_dates=result.already_scheduled_dates,
            cancelled_dates=result.cancelled_dates,
            paused=result.paused,
        )
