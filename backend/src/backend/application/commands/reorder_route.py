import logging
from dataclasses import dataclass
from datetime import date

from backend.application.common import ensure_exists
from backend.application.policies.access import ensure_can_manage
from backend.application.vars import OrderId, TimeSlotId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRoutePlanGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReorderRouteCommand:
    delivery_date: date
    time_slot_id: TimeSlotId | None
    order_id: OrderId
    new_position: int


class ReorderRouteCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._route_plan_gateway = route_plan_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: ReorderRouteCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        route_plan = ensure_exists(
            await self._route_plan_gateway.load_by_date(
                shop_id=current_user.shop_id,
                delivery_date=command.delivery_date,
                time_slot_id=command.time_slot_id,
            ),
            "RoutePlan",
        )

        sequence = list(route_plan.order_sequence)

        if command.order_id not in sequence:
            return

        sequence.remove(command.order_id)
        pos = max(0, min(command.new_position, len(sequence)))
        sequence.insert(pos, command.order_id)

        route_plan.order_sequence = sequence
        await self._tr_manager.commit()
