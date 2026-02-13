import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.errors import LastTimeSlotError
from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.vars import TimeSlotId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteTimeSlotCommand:
    time_slot_id: TimeSlotId


class DeleteTimeSlotCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._time_slot_gateway = time_slot_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteTimeSlotCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(command.time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)

        time_slots_count = await self._time_slot_gateway.count_by_shop(
            time_slot.shop_id
        )
        if time_slots_count <= 1:
            raise LastTimeSlotError

        await self._time_slot_gateway.delete(time_slot)

        await self._tr_manager.commit()

        logger.info("Time slot %s deleted", command.time_slot_id)
