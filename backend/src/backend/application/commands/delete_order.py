import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_can_manage,
)
from backend.application.services.generated_order_lifecycle import (
    GeneratedOrderLifecycle,
)
from backend.application.vars import OrderId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteOrderCommand:
    order_id: OrderId
    pause_recurring_order: bool = False


class DeleteOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        generated_order_lifecycle: GeneratedOrderLifecycle,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._generated_order_lifecycle = generated_order_lifecycle
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteOrderCommand) -> None:
        logger.info(
            "Deleting order: order_id=%s",
            command.order_id,
        )

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        await self._generated_order_lifecycle.delete_order(
            command.order_id,
            current_user,
            pause_recurring_order=command.pause_recurring_order,
        )
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted order: id=%s",
            command.order_id,
        )
