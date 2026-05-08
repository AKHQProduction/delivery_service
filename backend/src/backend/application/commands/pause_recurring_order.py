from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import RecurringOrderId, RecurringOrderStatus
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class PauseRecurringOrderCommand:
    recurring_order_id: RecurringOrderId


class PauseRecurringOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._recurring_order_gateway = recurring_order_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: PauseRecurringOrderCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        recurring_order = ensure_exists(
            await self._recurring_order_gateway.load(
                command.recurring_order_id
            ),
            "RecurringOrder",
        )
        ensure_related_to_shop(current_user, recurring_order.shop_id)
        recurring_order.status = RecurringOrderStatus.PAUSED
        await self._tr_manager.flush()
        await self._tr_manager.commit()
