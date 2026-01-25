import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.interfaces import IdentityProvider, TransactionManager
from backend.application.interfaces.gateways.time_slot_gateway import (
    TimeSlotGateway,
)
from backend.application.policies.access import IsOwner
from backend.application.vars import TimeSlotId

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteTimeSlotCommand:
    time_slot_id: TimeSlotId


class DeleteTimeSlotCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        time_slot_gateway: TimeSlotGateway,
        tx: TransactionManager,
    ) -> None:
        self._idp = idp
        self._time_slot_gateway = time_slot_gateway
        self._tx = tx

    async def handle(self, command: DeleteTimeSlotCommand) -> None:
        current_user = await self._idp.current_user()

        if not IsOwner().is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s trying to delete time slot",
                current_user.user_id,
            )
            raise AccessDeniedError

        time_slot = await self._time_slot_gateway.load(command.time_slot_id)
        if time_slot is None:
            logger.warning("Time slot %s not found", command.time_slot_id)
            raise EntityNotFoundError(entity="TimeSlot")

        if time_slot.shop_id != current_user.shop_id:
            logger.warning(
                "Access denied for user %s trying to delete "
                "time slot %s from another shop",
                current_user.user_id,
                command.time_slot_id,
            )
            raise AccessDeniedError

        await self._time_slot_gateway.delete(command.time_slot_id)

        await self._tx.commit()

        logger.info("Time slot %s deleted", command.time_slot_id)
